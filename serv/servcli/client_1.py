from multiprocessing.managers import BaseManager
class QueueManager(BaseManager): pass
QueueManager.register('get_queue')
m = QueueManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
m.connect()
dico = m.get_queue()
print(type(dico))
dico.update({"remy": "coucou", "johan": "yo"})
dico.update({"salut":1})
print(dico)