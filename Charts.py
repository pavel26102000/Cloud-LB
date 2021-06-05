from Testing import *

line_types = ['-', '--', '-.', ':']

def GetChartForStd(ratio = 6, num_runs=20, name="std"):
    num_pms = [50, 75, 100, 150, 200, 250, 300, 400, 500]
    algorithms = [RoundRobin, OppotunisticAlgo, HottestToColdest, MyAlgorithm]
    results = []
    fig, ax = plt.subplots(nrows=1, ncols=1)
    for i in range(len(algorithms)):
        results.append([])
        for j in range(len(num_pms)):
            if i != len(algorithms) - 1:
                _, _, _, usage, _ = TEST(num_pms[j], num_pms[j] * ratio, RoundRobin, algorithms[i], num_runs, silence=True)
            else:
                _, _, _, usage, _ = TEST(num_pms[j], num_pms[j] * ratio, RoundRobin, algorithms[i], num_runs,  silence=True, my_algo=True)
            results[i].append(usage)
    colors = ["red", "green", "blue", "magenta"]
    algorithm_name = ["RoundRobin", "Оппортунистичесикй алгортим", "Hottest-to-Coldest", "Представленный алгоритм"]
    plt.title("Сравнение стандартного отклонения нагрузки для разных алгоритмов")
    for j in range(len(algorithms)):
        ax.plot(num_pms, results[j], line_types[j], color=colors[j], label=algorithm_name[j])
    ax.grid()
    ax.legend()
    ax.title.set_text("Стандартное отклонение при отношении " + str(ratio))
    ax.set_ylim(0, 0.1)
    plt.setp(ax, xlabel="Количество физичесих машин")
    plt.setp(ax, ylabel="Стандартное отклонение")
    plt.show()
    fig.savefig("charts/" + name)
    print(*results)
    print("\n\n")


def GetGraphForMigr(ratio=6, num_runs=20, name="mig"):
    num_pms = [50, 75, 100, 150, 200, 250, 300, 400, 500]
    results = []
    fig, ax = plt.subplots(nrows=1, ncols=1)
    for i in range(len(num_pms)):
        _, _, _, _, mig = TEST(num_pms[i], num_pms[i] * ratio, RoundRobin, HottestToColdest, num_runs, silence=True)
        results.append(mig[0])

    print(results)
    print("\n")

    ax.plot(num_pms, results, "--", color="blue", label="Hottest-to-Coldest")

    results = [[], []]
    for i in range(len(num_pms)):
        _, _, _, _, mig = TEST(num_pms[i], num_pms[i] * ratio, RoundRobin, MyAlgorithm, num_runs, silence=True, my_algo=True)
        n_m, n_m_b = mig
        results[0].append(n_m)
        results[1].append(n_m_b)
        
    ax.plot(num_pms, results[1], "-.", color="red", label="Этап балансировки в представленном алгоритме")
    ax.plot(num_pms, results[0], color="magenta", label="Общее число миграций в представленном алгоритме")
    ax.grid()
    ax.legend()
    ax.title.set_text("Количество миграций при отношении " + str(ratio))
    ax.set_ylim(ymin=0)

    plt.setp(ax, xlabel="Количество физичесих машин")
    plt.setp(ax, ylabel="Количество миграций")
    plt.show()
    fig.savefig("charts/" + name)

    print(*results)
    print("\n\n")


def GetGraphForConsBoth(first_algo, ratio=6, num_runs=20, name="cons"):
    num_pms = [50, 75, 100, 150, 200, 250, 300, 400, 500]
    results = [[], []]

    for i in range(len(num_pms)):
        _, diff, orig, _, _ = TEST(num_pms[i], num_pms[i] * ratio, first_algo, MyAlgorithm, num_runs, silence=True, my_algo=True)
        results[1].append(orig + diff)
        results[0].append(orig)

    labels = ["Исходный алгоритм", "Представленный алгоритм"]

    fig, ax = plt.subplots(nrows=1, ncols=1)
    for i in range(len(results)):
        color = "magenta" * i + "orange" * (1 - i)
        ax.plot(num_pms, results[i], "--", color=color, label=labels[i])

    ax.grid()
    ax.legend()
    ax.title.set_text("Сводобные хосты до и после консолидации при отношении " + str(ratio))
    ax.set_ylim(ymin=0)
    plt.setp(ax, xlabel="Количество физичесих машин")
    plt.setp(ax, ylabel="Количество свободных хостов")
    plt.show()
    fig.savefig("charts/" + name)

    print(*results)
    print("\n\n")
