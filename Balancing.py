import numpy as np

from copy import deepcopy
import heapq


class Heap(object):
    def __init__(self, initial=None, key=lambda x: x):
        self.key = key
        self.index = 0
        if initial:
            self._data = [(key(item), i, deepcopy(item)) for i, item in enumerate(initial)]
            self.index = len(self._data)
            heapq.heapify(self._data)
        else:
            self._data = []

    def __len__(self):
        return len(self._data)

    def push(self, item, index=None):
        if index is None:
            heapq.heappush(self._data, (self.key(item), self.index, item))
            self.index += 1
        else:
            heapq.heappush(self._data, (self.key(item), index, item))

    def pop(self):
        return heapq.heappop(self._data)[1:]

    def empty(self):
        return len(self._data) == 0


def FFD(pms, vms, placement, sort_key=lambda x: -x.traits["ram"] * x.load["ram"]):
    for pm in pms:
        pm.clear()
    sorted_vms = list(enumerate(vms))
    sorted_vms.sort(key=lambda x: sort_key(x[1]))
    num_migrations = 0

    for i in range(len(sorted_vms)):
        vm_idx = sorted_vms[i][0]
        for j in range(len(pms)):
            if pms[j].check_vm(vms[vm_idx]):
                pms[j].place_vm(vms[vm_idx], vm_idx)

                if placement[j][vm_idx] != 1:
                    num_migrations += 1
                    for t in range(len(placement)):
                        placement[t][vm_idx] = 0
                    placement[j][vm_idx] = 1
                break

    return placement, num_migrations


def RoundRobinStarting(pms, vms, placement):
    idx = np.random.randint(0, len(pms) - 1)
    for i in range(len(vms)):
        temp = idx
        while True:
            if pms[idx].check_vm(vms[i]):
                placement[idx][i] = 1
                pms[idx].place_vm(vms[i], i)
                break
            idx += 1
            idx %= len(pms)
            if idx == temp:
                return placement[:, :i], vms[:i]
        idx = temp + 1
        idx %= len(pms)
    return placement, vms


def RoundRobin(pms, vms, placement):
    for pm in pms:
        pm.clear()
    num_migrations = 0

    idx = np.random.randint(0, len(pms) - 1)
    for i in range(len(vms)):
        temp = idx
        while True:
            if pms[idx].check_vm(vms[i]):
                if placement[idx][i] != 1:
                    num_migrations += 1
                    for t in range(len(placement)):
                        placement[t][i] = 0
                    placement[idx][i] = 1
                pms[idx].place_vm(vms[i], i)
                break
            idx += 1
            idx %= len(pms)
            if idx == temp:
                break
        idx = temp + 1
        idx %= len(pms)
    return placement, num_migrations


def OppotunisticAlgo(pms, vms, placement, sort_vm_key=lambda x: x.traits["ram"] * x.load["ram"],
                     sort_pm_key=lambda x: x.mean_load()):
    for pm in pms:
        pm.clear()

    num_migrations = 0
    pm_min_heap = Heap(initial=pms, key=sort_pm_key)
    MAX_PMS_TO_CONSIDER = 3

    for i in range(len(vms)):
        considered = 0
        to_return = []
        while considered < MAX_PMS_TO_CONSIDER:
            pm_idx, pm = pm_min_heap.pop()
            considered += 1
            placed = False

            if pms[pm_idx].check_vm(vms[i]):
                pms[pm_idx].place_vm(vms[i], i)
                pm.place_vm(vms[i], i)

                if placement[pm_idx][i] != 1:
                    num_migrations += 1
                    for t in range(len(placement)):
                        placement[t][i] = 0
                    placement[pm_idx][i] = 1
                placed = True
            to_return.append([pm, pm_idx])

            if placed:
                break

        for pm, pm_idx in to_return:
            pm_min_heap.push(pm, pm_idx)

    return placement, num_migrations


# this algorithm is designed only to get rid of overloaded hosts using the least possible amount of migrations
def HottestToColdest(pms, vms, placement, sort_vm_key=lambda x: x.traits["ram"] * x.load["ram"],
                     sort_pm_key=lambda x: x.mean_load() + x.is_overloaded()):
    pms_heap = Heap(pms, sort_pm_key)
    num_migrations = 0

    for i in range(len(pms)):
        if pms[i].is_overloaded():
            pms[i].vms.sort(key=lambda x: sort_vm_key(x[0]))

            to_insert_back = []
            curr_vm = -1
            while pms[i].is_overloaded():
                _, vm_idx = pms[i].vms[curr_vm]
                if pms_heap.empty():
                    for idx in to_insert_back:
                        pms_heap.push(pms[idx], idx)
                    to_insert_back = []
                    curr_vm -= 1
                    if curr_vm == -len(pms[i].vms):
                        print("Its Impossible for pm", i)
                        break
                    else:
                        continue
                target, _ = pms_heap.pop()
                to_insert_back.append(target)

                if pms[target].check_vm(vms[vm_idx]):
                    pms[i].remove_vm(vm_idx)
                    pms[target].place_vm(vms[vm_idx], vm_idx)
                    placement[i][vm_idx] = 0
                    placement[target][vm_idx] = 1
                    num_migrations += 1
                    for idx in to_insert_back:
                        pms_heap.push(pms[idx], idx)
                    to_insert_back = []
                    curr_vm = -1

    return placement, num_migrations


def MyAlgorithm(pms, vms, placement, sort_vm_key=lambda x: -x.max_relative_demand(),
                sort_pm_key=lambda x: x.max_relative_load(), max_migrations_to_free=5):
    have_to_migrate = Heap(key=sort_vm_key)
    low_load = [False] * len(pms)
    num_migrations = 0
    num_overloaded = 0

    for i in range(len(pms)):
        if pms[i].is_overloaded():
            num_overloaded += 1
            pms[i].vms.sort(key=lambda x: sort_vm_key(x[0]))
            while pms[i].is_overloaded():
                vm, vm_idx = pms[i].vms[-1]
                pms[i].remove_vm(vm_idx)
                placement[i][vm_idx] = 0
                have_to_migrate.push(vm, vm_idx)
        elif 0 < len(pms[i].vms) <= max_migrations_to_free:
            low_load[i] = True

    sorted_pms = sorted(enumerate(pms), key=lambda x: (len(x[1].vms) == 0, low_load[x[0]], sort_pm_key(x[1])))

    while not have_to_migrate.empty():
        vm_idx, vm = have_to_migrate.pop()
        for i in range(len(sorted_pms)):
            pm_idx = sorted_pms[i][0]
            if pms[pm_idx].check_vm(vm):
                pms[pm_idx].place_vm(vm, vm_idx)

                for t in range(len(pms)):
                    placement[t][vm_idx] = 0
                placement[pm_idx][vm_idx] = 1
                num_migrations += 1
                low_load[pm_idx] = False
                break

    num_migrations_balancing = num_migrations

    sorted_pms = sorted(enumerate(pms), key=lambda x: (len(x[1].vms) == 0, low_load[x[0]], sort_pm_key(x[1])))
    starting_idx = 0
    for i in range(len(low_load)):
        if low_load[i]:
            new_pm_idxes = []
            can_be_placed = True
            for vm, vm_idx in pms[i].vms:
                if can_be_placed:
                    j = (starting_idx + 1) % len(sorted_pms)
                    while j != starting_idx:
                        pm_idx = sorted_pms[j][0]
                        if pm_idx != i:
                            if len(pms[pm_idx].vms) == 0:
                                can_be_placed = False
                                j = 0
                                continue
                            if pms[pm_idx].check_vm(vm):
                                pms[pm_idx].place_vm(vm, vm_idx)
                                new_pm_idxes.append((pm_idx, vm_idx))
                                low_load[pm_idx] = False
                                starting_idx = j
                                break
                        if j < len(sorted_pms) - 1:
                            j += 1
                        else:
                            j = 0

            if can_be_placed:
                pms[i].clear()

                # deleting free pm from the list of possible targets for further migration
                for j in range(len(sorted_pms)):
                    if sorted_pms[j][0] == i:
                        sorted_pms.pop(j)
                        break

                for pm_idx, vm_idx in new_pm_idxes:
                    for t in range(len(pms)):
                        placement[t][vm_idx] = 0
                    placement[pm_idx][vm_idx] = 1
                    num_migrations += 1
            else:
                for pm_idx, vm_idx in new_pm_idxes:
                    pms[pm_idx].remove_vm(vm_idx)

    return placement, num_migrations_balancing, num_migrations
