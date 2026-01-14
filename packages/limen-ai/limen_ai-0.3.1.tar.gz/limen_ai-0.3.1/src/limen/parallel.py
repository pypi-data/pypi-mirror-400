"""
Parallel knowledge extraction for LIMEN-AI.

Provides multiprocessing support for batch document ingestion.
"""

import multiprocessing as mp
import json
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from queue import Empty

from .orchestrator import KnowledgeProposal


@dataclass
class ExtractionTask:
    """Task for parallel extraction worker."""
    doc_id: str
    text: str
    max_chars: int = 0


@dataclass
class ExtractionResult:
    """Result from parallel extraction."""
    doc_id: str
    success: bool
    proposal: Optional[KnowledgeProposal] = None
    error: Optional[str] = None
    

def _extraction_worker(
    task_queue: mp.Queue,
    result_queue: mp.Queue,
    model_name: str,
    temperature: float,
    max_new_tokens: int,
    worker_id: int
):
    """
    Worker process for parallel extraction.
    
    Runs in separate process, initializes own LimenClient.
    """
    from .orchestrator import LimenClient
    
    client = LimenClient(
        model_name=model_name,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        use_real_llm=True
    )
    
    while True:
        try:
            task = task_queue.get(timeout=5.0)
            if task is None:  # Poison pill
                break
            
            text = task.text
            if task.max_chars > 0 and len(text) > task.max_chars:
                text = text[:task.max_chars]
            
            try:
                proposal = client.extract(text)
                result = ExtractionResult(
                    doc_id=task.doc_id,
                    success=True,
                    proposal=proposal
                )
            except Exception as e:
                result = ExtractionResult(
                    doc_id=task.doc_id,
                    success=False,
                    error=str(e)
                )
            
            result_queue.put(result)
            
        except Empty:
            continue
        except KeyboardInterrupt:
            break


class ParallelExtractor:
    """
    Parallel document extraction coordinator.
    
    Usage:
        extractor = ParallelExtractor(num_workers=4, model_name="ollama/llama3.1:8b")
        proposals = extractor.extract_batch(documents)
    """
    
    def __init__(
        self,
        num_workers: int = 4,
        model_name: str = "ollama/llama3.1:8b",
        temperature: float = 0.1,
        max_new_tokens: int = 1024
    ):
        self.num_workers = num_workers
        self.model_name = model_name
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
    
    def extract_batch(
        self,
        documents: Dict[str, str],
        max_chars: int = 0,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Optional[KnowledgeProposal]]:
        """
        Extract knowledge from batch of documents in parallel.
        
        Args:
            documents: Dict mapping doc_id -> text
            max_chars: Truncate documents to this length (0 = no limit)
            progress_callback: Called with (completed, total) on each completion
        
        Returns:
            Dict mapping doc_id -> KnowledgeProposal (None if extraction failed)
        """
        task_queue = mp.Queue(maxsize=self.num_workers * 2)
        result_queue = mp.Queue()
        
        # Start workers
        workers = []
        for i in range(self.num_workers):
            p = mp.Process(
                target=_extraction_worker,
                args=(
                    task_queue,
                    result_queue,
                    self.model_name,
                    self.temperature,
                    self.max_new_tokens,
                    i
                )
            )
            p.start()
            workers.append(p)
        
        # Feed tasks
        total = len(documents)
        for doc_id, text in documents.items():
            task = ExtractionTask(doc_id=doc_id, text=text, max_chars=max_chars)
            task_queue.put(task)
        
        # Send poison pills
        for _ in range(self.num_workers):
            task_queue.put(None)
        
        # Collect results
        results = {}
        completed = 0
        
        while completed < total:
            try:
                result = result_queue.get(timeout=30.0)
                results[result.doc_id] = result.proposal if result.success else None
                completed += 1
                
                if progress_callback:
                    progress_callback(completed, total)
                    
            except Empty:
                # Check if workers died
                alive = sum(1 for p in workers if p.is_alive())
                if alive == 0:
                    break
        
        # Cleanup
        for p in workers:
            p.join(timeout=5.0)
            if p.is_alive():
                p.terminate()
        
        return results

