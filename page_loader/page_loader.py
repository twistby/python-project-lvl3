"""Page loader module."""
import logging
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


class AppInternalError(Exception):
    """Internal error class."""


class CreateDirError(AppInternalError):
    """Internal error class: create directory."""


class SavePageError(AppInternalError):
    """Internal error class: save file."""


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
            n=re.sub(LINK_RE_PATTERN, '-', link),  # noqa: W605
            e=extension,
        )
    return file_name


def save_page(
    page_address: str,
    page_text: str,
    save_directory: str,
) -> str:
    """Save web page."""
    page_name = form_file_name(page_address, HTML_EXT)

    full_path = os.path.join(save_directory, page_name)
    try:
        page_file = open(full_path, 'w')  # noqa: WPS515
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't save page. {em}".format(em=err)
        logging.error(err_msg)
        raise SavePageError(err_msg) from err
    else:
        with page_file:
            page_file.write(page_text)

    return full_path


def get_page_text(page_address: str) -> str:  # noqa: WPS238
    """Try get page text."""
    try:  # noqa: WPS229
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


def download(page_address: str, saving_directory: str = '') -> str:
    """Download page."""
    if not saving_directory:
        saving_directory = os.getcwd()
    if not urlparse(page_address).scheme:
        logging.warning('Looks like URL without scheme, "http://" added')
        page_address = 'http://{pa}'.format(pa=page_address)

    page_text = get_page_text(page_address)

    resource_dir = form_file_name(page_address, DIR_EXT)
    full_dir_name = os.path.join(saving_directory, resource_dir)
    if not os.path.exists(full_dir_name):
        try:
            os.makedirs(full_dir_name)
        except OSError as err:
            logging.debug(err)
            err_msg = "Can't create directory. {em}".format(em=err)
            logging.error(err_msg)
            raise CreateDirError(err_msg) from err

    page_text = download_resurces(
        page_text,
        page_address,
        saving_directory,
        resource_dir,
    )

    return save_page(page_address, page_text, saving_directory)
