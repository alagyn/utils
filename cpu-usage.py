import time

prev_total = None
prev_work = None

USER = 0
NICE = 1
SYSTEM = 2
IDLE = 3
IOWAIT = 4
IRQ = 5
SOFTIRQ = 6
STEAL = 7
GUEST = 8
GUEST_NICE = 9

while True:
    with open('/proc/stat', mode='r') as f:
        data = f.readlines()

    # total_line = data[0].strip().split()
    core_lines = list(filter(lambda x: x.startswith("cpu"), data[1:]))

    if prev_total is None:
        prev_total = [0] * len(core_lines)
        prev_work = [0] * len(core_lines)

    usage = [0] * len(core_lines)

    for idx, line in enumerate(core_lines):
        vals = [int(x) for x in line.strip().split()[1:]]

        work = vals[USER] + vals[NICE] + vals[SYSTEM]
        total = sum(vals)

        work_over_period = work - prev_work[idx]
        total_over_period = total - prev_total[idx]
        if total_over_period == 0:
            usage[idx] = 0
        else:
            usage[idx] = work_over_period / total_over_period

        prev_work[idx] = work
        prev_total[idx] = total

    for x in usage:
        print(f'{x:.3f}', end=" ")
    print()
    time.sleep(1)
