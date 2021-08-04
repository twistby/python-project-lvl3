"""Page-loader script."""
from page_loader.cli import get_args
from page_loader.page_loader import DEFAULT_SAVE_DIR, download


def main():
    """Run main function."""
    args = get_args(DEFAULT_SAVE_DIR)
    print(download(args.page_address, args.output))


if __name__ == '__main__':
    main()
