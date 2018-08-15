from collections import defaultdict, MutableSequence
import random
from typing import TypeVar, List, Tuple

T = TypeVar('T')

class OutOfIndexException(BaseException): pass

class EmptyArrayNotAcceptable(BaseException): pass

class NotifyUndependentItem(BaseException): pass

def pickOutItemFromArrayListUseSwap(arr: List[T], idx: int) -> T:
    if len(arr) == 0:
        raise EmptyArrayNotAcceptable

    if idx >= len(arr):
        raise OutOfIndexException

    item = arr[idx]
    arr[idx] = arr[-1]
    arr.pop()
    return item

def loopcheck(dependencies: List[Tuple[T, T]]):
    # TODO
    return False

class ShuffableListWithDependencies(list):
    def __init__(self, l: List[T], dependencies: List[Tuple[T, T]]):
        list.__init__(self, l)
        if (len(set(l)) != len(l)):
            raise Exception("l should have distinct values")

        if (loopcheck(dependencies)):
            raise Exception("loop detected")

        self.l = l
        self.dependencies = dependencies

    def shuffle(self):
        forwardMap = defaultdict(set)
        backwardMap = defaultdict(set)
        shuffled = []
        for dependency in self.dependencies:
            forwardMap[dependency[0]].add(dependency[1])
            backwardMap[dependency[1]].add(dependency[0])

        trackers = dict([ (n, DependencyMatchTracker(n, backwardMap[n])) for n in self.l ])

        toShuffle = ShuffableListWithDependencies(list(filter(lambda i: len(backwardMap[i]) == 0, self.l)), self.dependencies)

        while len(shuffled) != len(self.l):
            pickoutIdx = int(random.random() * len(toShuffle)) 
            pickOut = pickOutItemFromArrayListUseSwap(toShuffle, pickoutIdx)

            shuffled.append(pickOut)
            for i in forwardMap[pickOut]:
                trackers[i].notifyMatch(pickOut)
                if trackers[i].matched():
                    toShuffle.append(i)

        return shuffled


class DependencyMatchTracker:
    def __init__(self, item: T, dependencies: List[T]):
        self.item = item
        self.dependencies = { n for n in dependencies }
        self.matchedDependencies = set()

    def matched(self) -> bool:
        return len(self.matchedDependencies) == len(self.dependencies)

    def notifyMatch(self, dependency: T):
        if (dependency not in self.dependencies):
            raise NotifyUndependentItem

        self.matchedDependencies.add(dependency)


if __name__ == "__main__":
    sl = ShuffableListWithDependencies([1, 2, 3, 4, 5, 6], [(2, 4), (4, 6)])
    situations = {}
    for _ in range(1000):
        afterShuffle = sl.shuffle()  
        afterShuffleString = str(afterShuffle)
        if (situations.get(afterShuffleString, None)) is not None: 
            situations[afterShuffleString] += 1
        else:
            situations[afterShuffleString] = 1
        
        assert str(list(filter(lambda i: i in {2, 4, 6}, afterShuffle))) == str([2, 4, 6])
    assert(len(situations) > 50)
    print("all passed")

