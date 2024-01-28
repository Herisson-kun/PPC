class Lock:
    def __init__(self):
        self.value = 1

    def acquire(self):
        while not self._try_acquire():
            pass

    def _try_acquire(self):
        current_value = self.value
        new_value = current_value - 1

        if current_value > 0:
            self.value = new_value
            return True
        else:
            return False

    def release(self):
        self.value += 1