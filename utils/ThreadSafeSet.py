


from threading import Lock
class ThreadSafeSet:
    def __init__(self, timeout=None):
        self._set = set()
        self.lock = Lock()
        self._timeout = timeout  # second

    def add(self, item):
        if self.lock.acquire(timeout=self._timeout):
            self._set.add(item)
            self.lock.release()
            return True
        # else:
        #   raise TimeoutError("Failed to acquire lock within the specified timeout")
        return False

    def remove(self, item):
        if self.lock.acquire(timeout=self._timeout):
            if item in self._set:
                self._set.remove(item)
            self.lock.release()
            return True
        return False

    def __contains__(self, item):
        if self.lock.acquire(timeout=self._timeout):
            if item in self._set:
                self.lock.release()
                return True
            else:
                self.lock.release()
                return False
        return False

    def __len__(self):
        with self.lock:
            return len(self._set)

