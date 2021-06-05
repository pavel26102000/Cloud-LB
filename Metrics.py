import numpy as np

def CountOverloaded(pms):
    num_overloaded = 0
    for pm in pms:
        for trait in pm.traits:
            if pm.demand[trait] > pm.traits[trait] * pm.max_load[trait]:
                num_overloaded += 1
                break
    return num_overloaded


def CountStdResourceUsage(pms):
    usage = []
    for pm in pms:
        pm_usage = pm.mean_load()
        if pm_usage != 0:
            usage.append(pm_usage)
    return np.std(usage)


def CountFreePMS(placement):
    num_free = 0
    for i in range(len(placement)):
        if (placement[i] == 0).all():
            num_free += 1
    return num_free

def CheckCorrectness(placement):
    for j in range(len(placement[0])):
        is_placed = False
        for i in range(len(placement)):
            if placement[i][j] == 1:
                is_placed = True
                break
        if not is_placed:
            return False
    return True
