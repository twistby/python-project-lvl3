"""Page loader module."""
import os
import re
from urllib.parse import urlparse

import requests
from fake_useragent import UserAgent  # type: ignore

from page_loader.resourse_loader import LINK_RE_PATTERN, download_resurces

ua = UserAgent()
DEFAULT_HEADER = {'User-Agent': ua.random}  # noqa: WPS407
HTML_EXT = '.html'
DIR_EXT = '_files'


class WrongURLError(Exception):
    """Worng url exeption."""

    def __init__(self, *args):
        """Init class."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Return error."""
        if self.message:
            return 'WrongURLError, {0} '.format(self.message)
        return 'WrongURLError has been raised'


def form_file_name(
    page_adress: str,
    extension: str = '',
) -> str:
    """Form file name from link."""
    parsed_page = urlparse(page_adress)
    file_name = ''
    if parsed_page.hostname:
        link = '{h}{p}'.format(h=parsed_page.hostname, p=parsed_page.path)
        file_name = '{n}{e}'.format(
            n=re.sub(LINK_RE_PATTERN, '-', link),  # noqa: W605
            e=extension,
        )
    else:
        raise WrongURLError("Can't find host name in url!")
    return file_name


def save_page(
    page_adress: str,
    save_directory: str,
) -> str:
    """Save web page."""
    if not os.path.exists(save_directory) or not os.path.isdir(save_directory):
        raise ValueError(
            'The directory {wd} does not exist or is not a directory!'.format(
                wd=save_directory,
            ),
        )

    page_name = form_file_name(page_adress, HTML_EXT)
    response = requests.get(url=page_adress, headers=DEFAULT_HEADER)
    if response.ok:
        full_path = os.path.join(save_directory, page_name)
        with open(full_path, 'w') as page_file:
            page_file.write(response.text)
            page_file.close()
    else:
        raise requests.ConnectionError
    return full_path


def download(page_adress: str, save_directory: str = '') -> str:
    """Download page."""
    if not save_directory:
        save_directory = os.getcwd()

    local_page_path = save_page(page_adress, save_directory)

    resource_dir = form_file_name(page_adress, DIR_EXT)
    full_dir_name = os.path.join(save_directory, resource_dir)
    if not os.path.exists(full_dir_name):
        os.makedirs(full_dir_name)

    download_resurces(
        local_page_path,
        page_adress,
        save_directory,
        resource_dir,
        DEFAULT_HEADER,
    )
    return local_page_path
