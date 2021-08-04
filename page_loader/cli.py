"""Cli modul."""
import argparse


def make_parser(default_folder: str):
    """Make argparse parser."""
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument(
        'page_address',
        help='webpage address',
    )
    parser.add_argument(
        '-o',
        '--output',
        help='directory where to save the page',
        default=default_folder,
    )
    return parser


def get_args(default_folder: str):
    """Return arguments."""
    parser = make_parser(default_folder)
    return parser.parse_args()
