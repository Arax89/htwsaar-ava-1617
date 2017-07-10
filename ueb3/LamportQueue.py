from queue import PriorityQueue

pqueue = PriorityQueue()
pqueue.put((2, 1))
pqueue.put((1, 2))
pqueue.put((4, 2))
pqueue.put((1, 1))
pqueue.put((4, 1))
pqueue.put((3, 1))

while pqueue.qsize():
    print(pqueue.get())

exit()