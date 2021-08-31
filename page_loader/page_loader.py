"""Page loader module."""
import os
from urllib.parse import urlparse
from urllib.request import urlopen

DEFAULT_SAVE_DIR = os.getcwd()


def form_file_name(link: str) -> str:
    """Form file name from link."""
    file_name = ''
    if link:
        scheme = '{sc}://'.format(sc=urlparse(link).scheme)
        link_without_scheme = link.replace(scheme, '')
        file_name_symbols = []
        for symbol in link_without_scheme:
            if symbol.isalpha() or symbol.isdigit():
                file_name_symbols.append(symbol)
            else:
                file_name_symbols.append('-')
        file_name = '{lnk}.html'.format(lnk=''.join(file_name_symbols))
    return file_name


def download(page_adress: str, save_directory: str = DEFAULT_SAVE_DIR) -> str:
    """Download page."""
    if os.path.exists(save_directory) and os.path.isdir(save_directory):
        page = urlopen(page_adress)  # noqa: S310
        page_content = page.read().decode('utf-8')
        page_name = form_file_name(page_adress)
        full_path = os.path.join(save_directory, page_name)
        with open(full_path, 'w') as page_file:
            page_file.write(page_content)
            page_file.close()
        return full_path
    raise ValueError(
        'The directory {wd} does not exist or is not a directory!'.format(
            wd=save_directory,
        ),
    )
