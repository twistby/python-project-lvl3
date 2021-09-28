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
    return file_name


def save_page(
    page_adress: str,
    save_directory: str,
) -> str:
    """Save web page."""
    if not os.path.exists(save_directory) or not os.path.isdir(save_directory):
        err_msg = "Directory {wd} not exist or it's not a directory!".format(
            wd=save_directory,
        )
        logging.error(err_msg)
        raise ValueError(err_msg)
    elif not os.access(save_directory, os.W_OK):
        err_msg = 'No rights to save in {wd}'.format(
            wd=save_directory,
        )
        logging.error(err_msg)
        raise ValueError(err_msg)

    page_name = form_file_name(page_adress, HTML_EXT)

    page_text = get_page_text(page_adress)
    full_path = os.path.join(save_directory, page_name)
    with open(full_path, 'w') as page_file:
        page_file.write(page_text)
        page_file.close()
    return full_path


def get_page_text(page_adress: str) -> str:
    """Try get page text."""
    try:
        response = requests.get(url=page_adress, headers=DEFAULT_HEADER)
    except requests.exceptions.ConnectionError as err:
        logging.debug(err)
        err_msg = 'Network problem. {em}'.format(em=err)
        logging.error(err_msg)
        raise ConnectionError(err_msg)
    except requests.exceptions.HTTPError as err:
        logging.debug(err)
        err_msg = 'Invalid HTTP response. {em}'.format(em=err)
        logging.error(err_msg)
        raise ConnectionError(err_msg)
    except Exception as err:
        logging.debug(err)
        err_msg = 'There was an error. {em}'.format(em=err)
        logging.error(err_msg)
        raise ConnectionError(err_msg)
    response.encoding = 'utf-8'
    return response.text


def download(page_adress: str, save_directory: str = '') -> str:
    """Download page."""
    if not save_directory:
        save_directory = os.getcwd()
    if not urlparse(page_adress).scheme:
        logging.warning('Looks like URL without scheme, "http://" added')
        page_adress = 'http://{pa}'.format(pa=page_adress)

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
