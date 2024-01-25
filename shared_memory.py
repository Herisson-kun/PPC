from multiprocessing.managers import BaseManager

dico = {}
class MemoryManager(BaseManager): pass
MemoryManager.register('get_memory', callable=lambda:dico)
m_serv = MemoryManager(address=('127.0.0.1', 50000), authkey=b'abracadabra')
s_serv = m_serv.get_server()
s_serv.serve_forever()