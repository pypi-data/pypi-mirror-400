import k3stopwatch

sw = k3stopwatch.StopWatch()

with sw.timer("rwoot"):
    for i in range(50):
        with sw.timer("inner_task"):
            print("do_inner_task(i)")
