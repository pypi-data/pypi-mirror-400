import argparse
from aphantasist.modules.img2txt import img2txt

def main():
    parser = argparse.ArgumentParser(prog="aphantasist")
    parser.add_argument("--version", action="version", version="%(prog)s v0.0.1")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    start_parser = subparsers.add_parser("start", help="✍️ Read images from `input` folder and write the texts to the `output` folder")
    args = parser.parse_args()
    if args.command == 'start':
        img2txt()

    return

if __name__ == "__main__":
    main()
