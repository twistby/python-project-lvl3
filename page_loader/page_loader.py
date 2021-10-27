"""Page loader module."""
import logging
import os
import re
from urllib.parse import urlparse

import requests
from fake_useragent import UserAgent  # type: ignore

from page_loader.resource_loader import LINK_RE_PATTERN, download_resurces

ua = UserAgent()
DEFAULT_HEADER = {'User-Agent': ua.random}
HTML_EXT = '.html'
DIR_EXT = '_files'


class AppInternalError(Exception):
    """Internal error class."""


class CreateDirError(AppInternalError):
    """Internal error class: create directory."""


class SavePageError(AppInternalError):
    """Internal error class: save file."""


class DirNotExistError(AppInternalError):
    """Internal error class: saving directory not exist."""


class AppConnectionError(AppInternalError):
    """Internal error class: connection error."""


def form_file_name(
    page_address: str,
    extension: str = '',
) -> str:
    """Form file name from link."""
    parsed_page = urlparse(page_address)
    file_name = ''
    if parsed_page.hostname:
        link = '{h}{p}'.format(h=parsed_page.hostname, p=parsed_page.path)
        file_name = '{n}{e}'.format(
            n=re.sub(LINK_RE_PATTERN, '-', link),
            e=extension,
        )
    return file_name


def save_page(
    page_address: str,
    page_code: str,
    save_directory: str,
) -> str:
    """Save web page."""
    page_name = form_file_name(page_address, HTML_EXT)

    full_path = os.path.join(save_directory, page_name)
    try:
        page_file = open(full_path, 'w')
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't save page. {em}".format(em=err)
        logging.error(err_msg)
        raise SavePageError(err_msg) from err
    else:
        with page_file:
            page_file.write(page_code)

    return full_path


def get_page_code(page_address: str) -> str:
    """Try get page text."""
    try:
        response = requests.get(url=page_address, headers=DEFAULT_HEADER)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.debug(err)
        err_msg = 'HTTP error. {em}'.format(em=err)
        logging.error(err_msg)
        raise AppConnectionError(err_msg) from err
    except requests.exceptions.ConnectionError as err:
        logging.debug(err)
        err_msg = 'Network problem. {em}'.format(em=err)
        logging.error(err_msg)
        raise AppConnectionError(err_msg) from err
    except requests.exceptions.RequestException as err:
        logging.debug(err)
        err_msg = 'There was an error. {em}'.format(em=err)
        logging.error(err_msg)
        raise AppConnectionError(err_msg) from err

    return response.text


def set_saving_dir(saving_directory: str) -> str:
    """Check saving directory and set default if necessary."""
    if not saving_directory:
        saving_directory = os.getcwd()
    if not os.path.exists(saving_directory):
        err_msg = 'Saving directory not exist: {d}'.format(d=saving_directory)
        logging.error(err_msg)
        raise DirNotExistError(err_msg)
    return saving_directory


def download(page_address: str, saving_directory: str = '') -> str:
    """Download page."""
    saving_directory = set_saving_dir(saving_directory)

    if not urlparse(page_address).scheme:
        logging.warning('Looks like URL without scheme, "http://" added')
        page_address = 'http://{pa}'.format(pa=page_address)

    page_code = get_page_code(page_address)

    resource_dir = form_file_name(page_address, DIR_EXT)
    full_dir_name = os.path.join(saving_directory, resource_dir)
    try:
        os.mkdir(full_dir_name)
    except FileExistsError as err:
        logging.debug(err)
        err_msg = 'Directory exist. {em}'.format(em=err)
        logging.error(err_msg)
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't create directory. {em}".format(em=err)
        logging.error(err_msg)
        raise CreateDirError(err_msg) from err

    page_code = download_resurces(
        page_code,
        page_address,
        saving_directory,
        resource_dir,
    )

    return save_page(page_address, page_code, saving_directory)
