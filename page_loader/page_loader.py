"""Page loader module."""
import logging
import os
import re
from typing import TextIO, Tuple
from urllib.parse import urlparse

import requests
from fake_useragent import UserAgent  # type: ignore

from page_loader import app_errors
from page_loader.resource_loader import LINK_RE_PATTERN, download_resurces

ua = UserAgent()
DEFAULT_HEADER = {'User-Agent': ua.random}
HTML_EXT = '.html'
DIR_SUFFIX = '_files'


def form_file_name(
    page_url: str,
    extension: str = '',
) -> str:
    """Form file name from link."""
    parsed_page = urlparse(page_url)
    file_name = ''
    if parsed_page.hostname:
        link = '{h}{p}'.format(h=parsed_page.hostname, p=parsed_page.path)
        file_name = '{n}{e}'.format(
            n=re.sub(LINK_RE_PATTERN, '-', link),
            e=extension,
        )
    return file_name


def save_page(
    page_url: str,
    page_code: str,
    save_directory: str,
) -> str:
    """Save web page."""
    page_name = form_file_name(page_url, HTML_EXT)

    full_path = os.path.join(save_directory, page_name)
    try:
        page_file = open(full_path, 'w')
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't save page. {em}".format(em=err)
        logging.error(err_msg)
        raise app_errors.SavePageError(err_msg) from err
    else:
        with page_file:
            page_file.write(page_code)

    return full_path


def get_page_html(page_url: str) -> str:
    """Try get page text."""
    try:
        response = requests.get(url=page_url, headers=DEFAULT_HEADER)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logging.debug(err)
        err_msg = 'There was an error. {em}'.format(em=err)
        logging.error(err_msg)
        raise app_errors.AppConnectionError(err_msg) from err

    return response.text


def set_saving_dir(saving_directory: str) -> str:
    """Check saving directory and set default if necessary."""
    if not saving_directory:
        saving_directory = os.getcwd()
    if not os.path.exists(saving_directory):
        err_msg = 'Saving directory not exist: {d}'.format(d=saving_directory)
        logging.error(err_msg)
        raise app_errors.DirNotExistError(err_msg)
    return saving_directory


def check_url_schema(page_url: str) -> str:
    """Add schema if need."""
    if not urlparse(page_url).scheme:
        logging.warning('Looks like URL without scheme, "http://" added')
        page_url = 'http://{pa}'.format(pa=page_url)
    return page_url


def open_page_file(
    saving_directory: str,
    page_url: str,
) -> Tuple[TextIO, str]:
    """Open file to save page."""
    page_path = os.path.join(
        saving_directory,
        form_file_name(page_url, HTML_EXT),
    )
    try:
        page_file = open(page_path, 'w')
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't save page. {em}".format(em=err)
        logging.error(err_msg)
        raise app_errors.SavePageError(err_msg) from err
    return page_file, page_path


def download(page_url: str, saving_directory: str = '') -> str:
    """Download page."""
    if not saving_directory:
        saving_directory = os.getcwd()

    page_file, page_path = open_page_file(saving_directory, page_url)

    resource_dir_name = form_file_name(page_url, DIR_SUFFIX)
    resource_dir_path = os.path.join(saving_directory, resource_dir_name)
    try:
        os.mkdir(resource_dir_path)
    except FileExistsError as err:
        logging.debug(err)
        err_msg = 'Directory exist. {em}'.format(em=err)
        logging.error(err_msg)
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't create directory. {em}".format(em=err)
        logging.error(err_msg)
        raise app_errors.CreateDirError(err_msg) from err

    page_url = check_url_schema(page_url)
    page_html = get_page_html(page_url)

    page_html = download_resurces(
        page_html,
        page_url,
        saving_directory,
        resource_dir_name,
    )

    with page_file:
        try:
            page_file.write(page_html)
        except OSError as err:
            logging.debug(err)
            err_msg = "Can't save page. {em}".format(em=err)
            logging.error(err_msg)
            raise app_errors.SavePageError(err_msg) from err

    return page_path
