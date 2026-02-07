from PIL import Image
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("size", type=int)
    parser.add_argument("iFile")
    parser.add_argument("oFile")

    args = parser.parse_args()

    img = Image.open(args.iFile)
    img = img.resize((args.size, args.size))
    img.save(args.oFile)
