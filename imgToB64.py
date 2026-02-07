from PIL import Image
from argparse import ArgumentParser
import base64

CHUNK_SIZE = 64

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("iFile")
    parser.add_argument("oFile")
    parser.add_argument("size", type=int)
    parser.add_argument("--as-str", action="store_true")

    args = parser.parse_args()

    img = Image.open(args.iFile)
    img = img.resize((args.size, args.size)).convert("RGBA")
    b = img.tobytes()
    print("Num Image Bytes", len(b))
    data = base64.b64encode(b)
    print("Num B64 bytes", len(data))
    with open(args.oFile, mode='wb') as f:
        if args.as_str:
            i = 0
            while i < len(data):
                f.write(b'"')
                f.write(data[i:i + CHUNK_SIZE])
                i += CHUNK_SIZE
                f.write(b'"\n')
