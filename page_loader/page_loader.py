"""Page loader module."""
import os
import re
from typing import Optional
from urllib.parse import ParseResult, urlparse
from urllib.request import urlopen, urlretrieve

from bs4 import BeautifulSoup  # type: ignore

DEFAULT_SAVE_DIR = os.getcwd()
HTML_EXT = '.html'
DIR_EXT = '_files'


def form_file_name(
    page_host: Optional[str],
    page_path: Optional[str],
    extension: str = '',
) -> str:
    """Form file name from link."""
    file_name = ''
    if page_host:
        link = '{h}{p}'.format(h=page_host, p=page_path)
        file_name = '{n}{e}'.format(
            n=re.sub('[^0-9a-zA-Z\s]+', '-', link),  # noqa: W605
            e=extension,
        )
    return file_name


def form_image_name(  # noqa: C901
    page_host: Optional[str],
    page_path: Optional[str],
) -> str:
    """Form file name from link."""
    file_name = ''
    if page_host and page_path:
        first_part = re.sub('[^0-9a-zA-Z\s]+', '-', page_host)  # noqa: W605
        if '/' not in page_path:
            new_path = '/{p}'.format(p=page_path)
        else:
            new_path = page_path
        second_part = re.sub('[^0-9a-zA-Z\s.]+', '-', new_path)  # noqa: W605
        file_name = '{f}{s}'.format(f=first_part, s=second_part)
    return file_name


def save_page(page_adress: str, save_directory: str, page_name: str) -> str:
    """Save page to disk."""
    page = urlopen(page_adress)  # noqa: S310
    page_content = page.read().decode('utf-8')
    full_path = os.path.join(save_directory, page_name)
    with open(full_path, 'w') as page_file:
        page_file.write(page_content)
        page_file.close()
    return full_path


def make_resourse_dir(save_directory: str, dir_name: str) -> None:
    """Create directory for page files."""
    full_dir_name = os.path.join(save_directory, dir_name)
    if not os.path.exists(full_dir_name):
        os.makedirs(full_dir_name)


def get_image_link(parsed_page: ParseResult, path: str) -> str:
    """Get image link."""
    if '/' in path:
        link = '{s}://{h}{p}'.format(
            s=parsed_page.scheme,
            h=parsed_page.hostname,
            p=path,
        )
    else:
        splitted_path = parsed_page.path.split('/')
        new_path = '/'.join(splitted_path[:-1])
        link = '{s}://{h}{pth}/{p}'.format(
            s=parsed_page.scheme,
            h=parsed_page.hostname,
            pth=new_path,
            p=path,
        )
    return link


def save_images(
    page_adress: str,
    parsed_page: ParseResult,
    save_directory: str,
    save_dir: str,
) -> None:
    """Save page images."""
    page = urlopen(page_adress)  # noqa: S310
    soup = BeautifulSoup(page, 'html.parser')
    images = soup.findAll(name='img')
    image_pathes = {image['src'] for image in images}
    for path in image_pathes:
        link = get_image_link(parsed_page, path)
        image_name = form_image_name(parsed_page.hostname, path)
        full_path = os.path.join(save_directory, save_dir, image_name)
        urlretrieve(link, full_path)  # noqa: S310


def download(page_adress: str, save_directory: str = DEFAULT_SAVE_DIR) -> str:
    """Download page."""
    if not os.path.exists(save_directory) or not os.path.isdir(save_directory):
        raise ValueError(
            'The directory {wd} does not exist or is not a directory!'.format(
                wd=save_directory,
            ),
        )
    parsed_page = urlparse(page_adress)
    page_host = parsed_page.hostname
    page_path = parsed_page.path
    page_name = form_file_name(page_host, page_path, HTML_EXT)
    full_path = save_page(page_adress, save_directory, page_name)
    dir_name = form_file_name(page_host, page_path, DIR_EXT)
    make_resourse_dir(save_directory, dir_name)
    save_images(
        page_adress,
        parsed_page,
        save_directory,
        dir_name,
    )
    return full_path
