import argparse
from pathlib import Path

from .api import Classifier


def print_result(line: str, top):
    print(f"[+] input: {line}")
    print(f"   [~] {'top guess':<11} = {top[0][0]}")
    for label, prob in top:
        print(f"      [=] {label:<8} = {prob:.3f}")


def main():
    parser = argparse.ArgumentParser(prog="whatenc")
    parser.add_argument("input", help="string or path to text file")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.9.0")
    args = parser.parse_args()

    print("[*] loading classifier")

    classifier = Classifier()

    path = Path(args.input)
    if path.exists() and path.is_file():
        try:
            with path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    top = classifier.predict(line)
                    print_result(line, top)
        except Exception as e:
            print(f"[!] failed to read file: {e}")
    else:
        top = classifier.predict(args.input)
        print_result(args.input, top)


if __name__ == "__main__":
    main()
