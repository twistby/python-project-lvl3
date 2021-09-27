"""Page-loader script."""
import os

from page_loader.cli import get_args
from page_loader.page_loader import download


def main():
    """Run main function."""
    args = get_args(os.getcwd())
    print(download(args.page_address, args.output))


if __name__ == '__main__':
    main()
