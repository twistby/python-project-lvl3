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
    image_host: Optional[str],
    image_path: Optional[str],
) -> str:
    """Form file name from link."""
    image_name = ''
    if image_host and image_path:
        first_part = re.sub('[^0-9a-zA-Z\s]+', '-', image_host)  # noqa: W605
        if '/' not in image_path:
            new_path = '/{p}'.format(p=image_path)
        else:
            new_path = image_path
        second_part = re.sub('[^0-9a-zA-Z\s.]+', '-', new_path)  # noqa: W605
        image_name = '{f}{s}'.format(f=first_part, s=second_part)
    return image_name


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
    page: str,
    parsed_page: ParseResult,
    save_directory: str,
    resource_dir: str,
) -> dict:
    """Save page images."""
    replacements = {}
    with open(page) as local_page:
        soup = BeautifulSoup(local_page, 'html.parser')
    images = soup.findAll(name='img')
    image_pathes = {image['src'] for image in images}
    for path in image_pathes:
        if urlparse(path).scheme == '':
            link = get_image_link(parsed_page, path)
            image_name = form_image_name(parsed_page.hostname, path)
            urlretrieve(  # noqa: S310
                link,
                os.path.join(save_directory, resource_dir, image_name),
            )
            replacements[path] = image_name
    return replacements


def replace_links(page: str, resource_dir: str, replace_data: dict) -> None:
    """Replace links to images in page."""
    with open(page) as local_page:
        soup = BeautifulSoup(local_page, 'html.parser')
    images = soup.findAll(name='img')
    for image in images:
        if replace_data.get(image['src']) is not None:
            image['src'] = os.path.join(
                resource_dir,
                str(replace_data.get(image['src'])),
            )
    with open(page, 'w') as new_page:
        new_page.write(soup.prettify())


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
    local_page_path = save_page(page_adress, save_directory, page_name)
    resource_dir = form_file_name(page_host, page_path, DIR_EXT)
    make_resourse_dir(save_directory, resource_dir)
    images = save_images(
        local_page_path,
        parsed_page,
        save_directory,
        resource_dir,
    )
    replace_links(local_page_path, resource_dir, images)
    return local_page_path
