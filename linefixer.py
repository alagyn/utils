import sys
import os.path

if __name__ == '__main__':
    # convert all files in arg list to have same line ending
    for file in sys.argv[1:]:
        if os.path.isfile(file):
            try:
                print(f"Fixing {file}")
                with open(file, mode='r') as f:
                    lines = [x.rstrip() for x in f.readlines()]
                with open(file, mode='wb') as f:
                    for line in lines:
                        f.write(bytes(line + "\n", "utf-8"))
            except:
                continue