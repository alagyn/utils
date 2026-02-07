#!/bin/python3
for i in range(128):
    if i % 8 == 0:
        print("")
    print(f"\x1B[{i}m{i:4d}\x1B[0m", end="")
