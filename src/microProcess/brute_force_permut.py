import time


class Permutation:
    slot_capacity = 5

    def __init__(self, left, mid, right, dropped, previous, dist, move=None):
        self.left, self.mid, self.right, self.dropped = left, mid, right, dropped
        self.previous, self.dist, self.move = previous, dist, move

    def neighbors(self):
        # if self.left == 'MJR':
        #     yield self.dist, '', self.mid, self.right, self.dropped + 1
        # if self.mid == 'MJR':
        #     yield self.dist, self.left, '', self.right, self.dropped + 1
        # if self.right == 'MJR':
        #     yield self.dist, self.left, self.mid, '', self.dropped + 1

        # if not self.left:
        #     for l in 'MJR':
        #         if l not in self.left + self.right + self.mid:
        #             yield self.dist, l * 3, self.mid, self.right, self.dropped
        #
        # if not self.right:
        #     for l in 'MJR':
        #         if l not in self.left + self.right + self.mid:
        #             yield self.dist, self.left, self.mid, l * 3, self.dropped
        # if not self.mid:
        #     for l in 'MJR':
        #         if l not in self.left + self.right + self.mid:
        #             yield self.dist, self.left, l * 3, self.right, self.dropped

        if self.left:
            if len(self.mid) < self.slot_capacity:
                yield self.dist + 1, self.left[:-1], self.mid + self.left[-1], self.right, self.dropped, (0, 1)
            if len(self.right) < self.slot_capacity:
                yield self.dist + 1, self.left[:-1], self.mid, self.right + self.left[-1], self.dropped, (0, 2)
        if self.mid:
            if len(self.left) < self.slot_capacity:
                yield self.dist + 1, self.left + self.mid[-1], self.mid[:-1], self.right, self.dropped, (1, 0)
            if len(self.right) < self.slot_capacity:
                yield self.dist + 1, self.left, self.mid[:-1], self.right + self.mid[-1], self.dropped, (1, 2)
        if self.right:
            if len(self.left) < self.slot_capacity:
                yield self.dist + 1, self.left + self.right[-1], self.mid, self.right[:-1], self.dropped, (2, 0)
            if len(self.mid) < self.slot_capacity:
                yield self.dist + 1, self.left, self.mid + self.right[-1], self.right[:-1], self.dropped, (2, 1)

    def get_key(self):
        return self.left, self.mid, self.right

    def __repr__(self):
        return '\n'.join((f'Distance : {self.dist}', repr(self.left), repr(self.mid), repr(self.right), f'Move: {self.move}'))


def dijkstra():
    start = Permutation('RRR', 'JJJ', 'MMM', 0, None, 0)
    queue = [start]

    visited = {start.get_key(): start}
    running = True
    while queue and running:
        print(f'\r{len(visited) = }; {len(queue) = }', end='')
        current = queue.pop(min(tuple(enumerate(queue)), key=lambda x: x[1].dist)[0])

        # if current.dropped == 3:
        #     print()
        #     return current

        if current.left == current.right == current.mid == 'MJR':
            return current

        for dist, left, mid, right, dropped, move in current.neighbors():
            nb = Permutation(left, mid, right, dropped, current, dist, move)
            key = nb.get_key()
            if key not in visited:
                visited[key] = nb
                queue.append(nb)
            elif dist < visited[key].dist:
                visited[key].dist = dist
                visited[key].previous = current


date = time.perf_counter()
res = dijkstra()
print('\n', time.perf_counter() - date, 's')
print('\n', res.dist, sep='')

route = []
while res.previous is not None:
    route.insert(0, res)
    res = res.previous

print(res, *route, sep='\n\n')


import json
with open('tri.json', 'w') as f:
    json.dump({
        'start': (res.left, res.mid, res.right),
        'steps': [
            '->'.join(map(str, perm.move)) for perm in route
        ]
    }, f, indent=4)
