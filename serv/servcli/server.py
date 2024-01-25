from multiprocessing.managers import BaseManager
from queue import Queue
list = dict()
class QueueManager(BaseManager): pass
QueueManager.register('get_queue', callable=lambda:list)
m = QueueManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
s = m.get_server()
s.serve_forever()