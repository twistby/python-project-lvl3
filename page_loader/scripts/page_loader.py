"""Page-loader script."""
import logging
import os
import sys

from page_loader.app_errors import AppInternalError
from page_loader.cli import get_args
from page_loader.page_loader import download


def main():
    """Run main function."""
    args = get_args(os.getcwd())
    try:
        file_path = download(args.page_address, args.output)
    except AppInternalError as err:
        print(err)  # noqa: WPS421
        sys.exit(1)
    except Exception as err:
        logging.error('Unknown error: {err}'.format(err=err))
        sys.exit(1)
    print('\n{p}'.format(p=file_path))  # noqa: WPS421
    sys.exit(0)


if __name__ == '__main__':
    main()
