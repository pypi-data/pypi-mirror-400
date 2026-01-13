import sys

from zorto.core import run_cli


def main() -> int:
    return run_cli(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
