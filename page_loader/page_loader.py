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
IMAGE_TAG = 'img'
LINK_TAG = 'link'
SCRIPT_TAG = 'script'
SRC_ATTR = 'src'
HREF_ATTR = 'href'
LINK_RE_PATTERN = '[^0-9a-zA-Z\s]+'  # noqa: W605
FILE_RE_PATTERN = '[^0-9a-zA-Z\s.]+'  # noqa: W605


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
            n=re.sub(LINK_RE_PATTERN, '-', link),  # noqa: W605
            e=extension,
        )
    return file_name


def form_resourse_name(  # noqa: C901
    res_path: Optional[str],
    res_host: Optional[str] = '',
) -> str:
    """Form file name from link."""
    resours_name = ''
    if res_host and res_path:
        first_part = re.sub(LINK_RE_PATTERN, '-', res_host)  # noqa: W605
        if '/' not in res_path:
            new_path = '/{p}'.format(p=res_path)
        else:
            new_path = res_path
        second_part = re.sub(FILE_RE_PATTERN, '-', new_path)  # noqa: W605
        resours_name = '{f}{s}'.format(f=first_part, s=second_part)
    return resours_name


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


def get_resourse_pathes(page):
    """Collect pathes of resourses."""
    with open(page) as local_page:
        soup = BeautifulSoup(local_page, 'html.parser')
    image_pathes = {tag[SRC_ATTR] for tag in soup.findAll(name=IMAGE_TAG)}
    link_pathes = {tag[HREF_ATTR] for tag in soup.findAll(name=LINK_TAG)}
    script_pathes = set()
    script_tags = soup.findAll(name=SCRIPT_TAG)
    for tag in script_tags:
        if tag.has_attr(SRC_ATTR):
            script_pathes.add(tag[SRC_ATTR])
    return image_pathes.union(link_pathes.union(script_pathes))


def save_resourses(
    page: str,
    parsed_page: ParseResult,
    save_directory: str,
    resource_dir: str,
) -> dict:
    """Save page resourses."""
    replacements = {}
    resours_pathes = get_resourse_pathes(page)
    for path in resours_pathes:
        parsed_path = urlparse(path)
        if parsed_path.scheme == '':
            resours_name = form_resourse_name(
                parsed_path.path,
                parsed_page.hostname,
            )
            urlretrieve(  # noqa: S310
                get_image_link(parsed_page, path),
                os.path.join(save_directory, resource_dir, resours_name),
            )
            replacements[path] = resours_name
        elif parsed_path.hostname == parsed_page.hostname:
            resours_name = form_resourse_name(
                parsed_path.path,
                parsed_path.hostname,
            )
            urlretrieve(  # noqa: S310
                path,
                os.path.join(save_directory, resource_dir, resours_name),
            )
            replacements[path] = resours_name
    return replacements


def change_tags(
    tags: set,
    atribute: str,
    replace_data: dict,
    res_dir: str,
) -> None:
    """Change tags attributs."""
    for tag in tags:
        if tag.has_attr(atribute):
            if replace_data.get(tag[atribute]) is not None:
                tag[atribute] = os.path.join(
                    res_dir,
                    str(replace_data.get(tag[atribute])),
                )


def replace_links(page: str, resource_dir: str, replace_data: dict) -> None:
    """Replace links to images in page."""
    with open(page) as local_page:
        soup = BeautifulSoup(local_page, 'html.parser')

    image_tags = soup.findAll(name=IMAGE_TAG)
    change_tags(image_tags, SRC_ATTR, replace_data, resource_dir)

    link_tags = soup.findAll(name=LINK_TAG)
    change_tags(link_tags, HREF_ATTR, replace_data, resource_dir)

    script_tags = soup.findAll(name=SCRIPT_TAG)
    change_tags(script_tags, SRC_ATTR, replace_data, resource_dir)

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
    resourses = save_resourses(
        local_page_path,
        parsed_page,
        save_directory,
        resource_dir,
    )
    replace_links(local_page_path, resource_dir, resourses)
    return local_page_path
