import time

class Permutation:
    def __init__(self, left, mid, right, dropped, previous, dist):
        self.left, self.mid, self.right, self.dropped = left, mid, right, dropped
        self.previous, self.dist = previous, dist

    def neighbors(self):
        if self.left == 'MJR':
            yield self.dist, '', self.mid, self.right, self.dropped + 1
        if self.mid == 'MJR':
            yield self.dist, self.left, '', self.right, self.dropped + 1
        if self.right == 'MJR':
            yield self.dist, self.left, self.mid, '', self.dropped + 1

        if self.left:
            if len(self.mid) < 4:
                yield self.dist + 1, self.left[:-1], self.mid + self.left[-1], self.right, self.dropped
            if len(self.right) < 4:
                yield self.dist + 1, self.left[:-1], self.mid, self.right + self.left[-1], self.dropped
        if self.mid:
            if len(self.left) < 4:
                yield self.dist + 1, self.left + self.mid[-1], self.mid[:-1], self.right, self.dropped
            if len(self.right) < 4:
                yield self.dist + 1, self.left, self.mid[:-1], self.right + self.mid[-1], self.dropped
        if self.right:
            if len(self.left) < 4:
                yield self.dist + 1, self.left + self.right[-1], self.mid, self.right[:-1], self.dropped
            if len(self.mid) < 4:
                yield self.dist + 1, self.left, self.mid + self.right[-1], self.right[:-1], self.dropped

        # slots = self.left, self.mid, self.right
        # for src in range(3):
        #     if not slots[src]:
        #         continue
        #     for des in range(2):
        #         if len(slots[src - des - 1]) < 5:
        #             yield self.dist + 1, *(slot[:-1] if i == src else slot + slots[src][-1] if i == (src - des - 1) % 3 else slot for i, slot in enumerate(slots)), self.dropped

    def get_key(self):
        return self.left, self.mid, self.right

    def __repr__(self):
        return '\n'.join((f'Distance : {self.dist}', repr(self.left), repr(self.mid), repr(self.right)))


def dijkstra():
    start = Permutation('MMM', 'RRR', 'JJJ', 0, None, 0)
    queue = [start]

    visited = {start.get_key(): start}
    running = True
    while queue and running:
        current = queue.pop(min(tuple(enumerate(queue)), key=lambda x: x[1].dist)[0])

        print(f'\r{len(visited) = }, {len(queue) = }, {current.dist = }', end='')
        display = False
        # if current.left == 'MJR' and not current.mid and not current.right:
        #     print(current)
        #     display = True

        if current.dropped == 3:
            return current

        for dist, left, mid, right, dropped in current.neighbors():
            nb = Permutation(left, mid, right, dropped, current, dist)
            if display:
                print('hey')
                print(nb)
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
