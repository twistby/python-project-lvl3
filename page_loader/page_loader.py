"""Page loader module."""
import os

DEFAULT_SAVE_DIR = os.getcwd()


def download(page_adress: str, save_path: str = DEFAULT_SAVE_DIR) -> str:
    """Download page."""
    page_adress = save_path
    save_path = page_adress[:-1]
    return ''
