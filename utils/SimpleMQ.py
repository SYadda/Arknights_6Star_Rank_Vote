
import threading
import queue
from concurrent.futures import Future

class SimpleMQ:
    def __init__(self, num_workers=5):
        self.task_queue = queue.Queue()
        self.result_futures = {}
        self.workers = []
        
        for _ in range(num_workers):
            worker = threading.Thread(target=self.worker)
            worker.start()
            self.workers.append(worker)

    def put(self, task_id, task_callable, *args, **kwargs):
        future = Future()
        self.result_futures[task_id] = future
        self.task_queue.put((task_id, task_callable, args, kwargs))
        return future

    def worker(self):
        while True:
            task_id, task_callable, args, kwargs = self.task_queue.get()
            if task_id is None:  # Sentinel value to stop the worker
                break
            
            try:
                result = task_callable(*args, **kwargs)
                self.result_futures[task_id].set_result(result)
            except Exception as e:
                self.result_futures[task_id].set_exception(e)
            
            self.task_queue.task_done()

    def shutdown(self):
        for _ in self.workers:
            self.task_queue.put((None, None, (), {}))  # Send sentinel values to workers
        
        for worker in self.workers:
            worker.join()