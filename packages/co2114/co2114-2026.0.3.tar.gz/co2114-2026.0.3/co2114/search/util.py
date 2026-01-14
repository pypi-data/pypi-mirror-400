from collections import deque

class queue:
    def __init__(self):
        self.data = deque()

    def __repr__(self):
        return str(list(self.data))
    
    def __iter__(self):
        return iter(self.data)

    def push(self, x):
        self.data.append(x)

    def pop(self):
        return self.data.popleft()

class stack(queue):
    def pop(self):
        return self.data.pop()
    

def manhattan(a, b):
    ax, ay = a  # (x, y)
    bx, by = b  # (x, y)
    return abs(bx-ax) + abs(by-ay)