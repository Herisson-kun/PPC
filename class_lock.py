class Lock:
    def __init__(self):
        self.value = 1

    def acquire(self):
        while not self._try_acquire():
            pass

    def _try_acquire(self):
        
        if self.value > 0:
            self.value = self.value -1
            return True
        else:
            return False

    def release(self):
        self.value += 1