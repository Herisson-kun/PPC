shared_mem = {"hands": {1: [1,2,3]}}
shared_mem.get("hands").get(1).remove(2)
print(shared_mem)