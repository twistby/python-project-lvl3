"""Page loader module."""
import logging
import os
import re
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
    addition: str = '',
) -> str:
    """Form file name from URL."""
    parsed_page = urlparse(page_url)
    file_name = ''
    if parsed_page.hostname:
        link = '{h}{p}'.format(h=parsed_page.hostname, p=parsed_page.path)
        file_name = '{n}{e}'.format(
            n=re.sub(LINK_RE_PATTERN, '-', link),
            e=addition,
        )
    return file_name


def get_page_html(page_url: str) -> str:
    """Try get page html."""
    try:
        response = requests.get(url=page_url, headers=DEFAULT_HEADER)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        logging.debug(err)
        err_msg = 'There was an error. {em}'.format(em=err)
        logging.error(err_msg)
        raise app_errors.AppConnectionError(err_msg) from err

    return response.text


def add_url_schema(page_url: str) -> str:
    """Add schema if need."""
    if not urlparse(page_url).scheme:
        logging.warning('Looks like URL without scheme, "http://" added')
        page_url = 'http://{pa}'.format(pa=page_url)
    return page_url


def save_page(
    saving_directory: str,
    page_file_name: str,
    page_html: str,
) -> str:
    """Save page to file."""
    page_path = os.path.join(saving_directory, page_file_name)
    try:
        page_file = open(page_path, 'w')
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't save page. {em}".format(em=err)
        logging.error(err_msg)
        raise app_errors.SavePageError(err_msg) from err

    with page_file:
        try:
            page_file.write(page_html)
        except OSError as err:
            logging.debug(err)
            err_msg = "Can't save page. {em}".format(em=err)
            logging.error(err_msg)
            raise app_errors.SavePageError(err_msg) from err

    return page_path


def download(page_url: str, saving_directory: str = '') -> str:
    """Download page."""
    if not saving_directory:
        saving_directory = os.getcwd()

    page_url = add_url_schema(page_url)
    page_html = get_page_html(page_url)

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

    page_html = download_resurces(
        page_html,
        page_url,
        saving_directory,
        resource_dir_name,
    )

    page_file_name = form_file_name(page_url, HTML_EXT)
    return save_page(saving_directory, page_file_name, page_html)
