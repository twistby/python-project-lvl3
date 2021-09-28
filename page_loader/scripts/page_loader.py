"""Page-loader script."""
import logging
import os
import sys

from page_loader.cli import get_args
from page_loader.page_loader import download


def main():
    """Run main function."""
    args = get_args(os.getcwd())
    try:
        file_path = download(args.page_address, args.output)
    except ValueError as err:
        print('Value error: {e}'.format(e=err))
        sys.exit(1)
    except ConnectionError as err:
        print('Connection error: {e}'.format(e=err))
        sys.exit(1)
    except Exception as err:
        logging.error('Unknown error: {err}'.format(err=err))
        sys.exit(1)
    print('\n{p}'.format(p=file_path))
    sys.exit(0)


if __name__ == '__main__':
    main()
