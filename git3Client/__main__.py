import sys
from .git3 import main


def run():
    """The main routine."""
    main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(run())
