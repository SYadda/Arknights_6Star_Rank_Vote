import threading
import time
from collections import OrderedDict
import concurrent.futures
import random

# 性能爆了，别用了
class ThreadSafeOrderedDict:
    def __init__(self, expiration_time):
        self._dict = OrderedDict()  # key: (value, expiration_time)
        self._lock = threading.Lock()
        self.expiration_time = expiration_time  # Time in seconds after which an item expires
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_items, daemon=True)
        self._cleanup_thread.start()

    def set_item(self, key, value, ttl=None):
        """Set an item with a specified TTL (Time To Live) or default expiration time."""
        expire_at = time.time() + (ttl if ttl is not None else self.expiration_time)
        with self._lock:
            self._dict[key] = (value, expire_at)

    def get_item(self, key):
        with self._lock:
            item = self._dict.get(key)
            if item and item[1] > time.time():
                return item[0]
            elif item:
                del self._dict[key]  # Remove expired item
            return None

    def delete_item(self, key):
        with self._lock:
            if key in self._dict:
                del self._dict[key]

    def _cleanup_expired_items(self):
        while True:
            current_time = time.time()
            with self._lock:
                keys_to_delete = [k for k, v in self._dict.items() if v[1] <= current_time]
                for k in keys_to_delete:
                    del self._dict[k]
            time.sleep(1)  # Sleep for 1 second before checking again

    def items(self):
        with self._lock:
            current_time = time.time()
            valid_items = {k: v[0] for k, v in self._dict.items() if v[1] > current_time}
            return list(valid_items.items())

def worker(ts_dict, num_operations):
    start_time = time.time()
    for _ in range(num_operations):
        action = random.choice(['set', 'get', 'delete'])
        key = f"key_{random.randint(1, 100)}"
        if action == 'set':
            ts_dict.set_item(key, f"value_{key}")
        elif action == 'get':
            ts_dict.get_item(key)
        elif action == 'delete':
            ts_dict.delete_item(key)
    end_time = time.time()
    return end_time - start_time

def run_concurrency_test(num_threads, num_operations_per_thread):
    ts_dict = ThreadSafeOrderedDict(expiration_time=5)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker, ts_dict, num_operations_per_thread) for _ in range(num_threads)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = sum(results)
    print(f"Total time taken by all threads: {total_time:.2f} seconds")
    print(f"Average time per thread: {total_time / num_threads:.2f} seconds")



# Total time taken by all threads: 12378844.40 seconds
# Average time per thread: 123.79 seconds

# if __name__ == "__main__":
    # # 示例使用
    # ts_dict = ThreadSafeOrderedDict()
    # ts_dict.set_item('key1', 'value1')
    # print(ts_dict.get_item('key1'))  # 输出: value1
    # ts_dict.delete_item('key1')
    # print(ts_dict.items())          # 输出: []

    # # 示例测试
    # num_threads = 100000
    # num_operations_per_thread = 100
    # run_concurrency_test(num_threads, num_operations_per_thread)