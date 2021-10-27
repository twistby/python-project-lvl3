"""Page resources loader module."""
import logging
import os
import re
from typing import BinaryIO, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import ResultSet  # type: ignore
from fake_useragent import UserAgent  # type: ignore
from progress.bar import Bar  # type: ignore
from requests.models import Response  # type: ignore

ua = UserAgent()
DEFAULT_HEADER = {'User-Agent': ua.random}
IMAGE_TAG = 'img'
LINK_TAG = 'link'
SCRIPT_TAG = 'script'
SRC_ATTR = 'src'
HREF_ATTR = 'href'
TAGS_ATTR = {
    IMAGE_TAG: SRC_ATTR,
    LINK_TAG: HREF_ATTR,
    SCRIPT_TAG: SRC_ATTR,
}
LINK_RE_PATTERN = '[^0-9a-zA-Z]+'
FILE_EXT_RE_PATTERN = '\.\w{0,}($|\?)'  # noqa: W605
CHUNK_SIZE = 1024


def get_extention(full_path: str) -> str:
    """Get extention from url or default."""
    file_extention_obj = re.search(
        FILE_EXT_RE_PATTERN,
        full_path,
        flags=re.IGNORECASE,
    )
    if file_extention_obj is None:
        file_extention = '.html'
    else:
        file_extention = file_extention_obj.group(0)
    return file_extention


def form_resource_name(resource_link: str) -> str:
    """Form file name from link."""
    parsed_url = urlparse(resource_link)
    link = '{a}{b}'.format(a=parsed_url.hostname, b=parsed_url.path)
    file_extention = get_extention(link)
    return '{p}{e}'.format(
        p=re.sub(LINK_RE_PATTERN, '-', link.replace(file_extention, '')),
        e=file_extention,
    )


def get_resource_urls(soup: BeautifulSoup) -> set:
    """Collect paths of resources."""
    return {
        tag[TAGS_ATTR[tag.name]]
        for tag in soup.findAll(name=list(TAGS_ATTR.keys()))
        if tag.has_attr(TAGS_ATTR[tag.name])
    }


def change_tags(
    tags: ResultSet,
    replace_data: dict,
    resource_dir: str,
) -> None:
    """Change tags attributs."""
    for tag in tags:
        atribute = TAGS_ATTR[tag.name]
        if tag.has_attr(atribute):
            if replace_data.get(tag[atribute]) is not None:
                new_resource_path = os.path.join(
                    resource_dir,
                    str(replace_data.get(tag[atribute])),
                )
                tag[atribute] = new_resource_path


def replace_links(
    soup: BeautifulSoup,
    resource_dir: str,
    replace_data: dict,
) -> str:
    """Replace links to resources in page text."""
    resource_tags = soup.findAll(name=list(TAGS_ATTR.keys()))
    change_tags(resource_tags, replace_data, resource_dir)
    return soup.prettify()


def is_local_res(
    url: str,
    resource_netloc: str,
    page_netlock: str,
) -> bool:
    """Check is resource local."""
    is_encoded = 'data:' in url
    is_local = not resource_netloc or resource_netloc == page_netlock
    return is_local and not is_encoded


def get_response(resource_link: str) -> Optional[Response]:
    """Get response from the resource link."""
    try:
        response = requests.get(
            url=resource_link,
            headers=DEFAULT_HEADER,
            stream=True,
        )
        response.raise_for_status()
    except requests.RequestException as err:
        logging.debug(
            'Something wrong with resource: {r}. {err}'.format(
                r=resource_link,
                err=err,
            ),
        )
        return None
    return response


def get_resource_file(
    save_directory: str,
    resource_dir: str,
    resource_name: str,
) -> Optional[BinaryIO]:
    """Try open file to save resource."""
    try:
        resource_file = open(
            os.path.join(save_directory, resource_dir, resource_name),
            'wb',
        )
    except OSError as err:
        logging.debug(err)
        err_msg = "Can't save resource . {em}".format(em=err)
        logging.error(err_msg)
        return None
    return resource_file


def save_resource(
    resource_file: BinaryIO,
    response: Response,
    replacements: dict,
    resource_name: str,
    path: str,
) -> None:
    """Try save resource to file."""
    with resource_file:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            try:
                resource_file.write(chunk)
            except OSError as err:
                logging.debug(err)
                err_msg = "Can't save resource {rm}. {em}".format(
                    rm=resource_name,
                    em=err,
                )
                logging.error(err_msg)
        replacements[path] = resource_name


def download_resurces(
    page_code: str,
    page_url: str,
    save_directory: str,
    resource_dir: str,
) -> str:
    """Download web-page resources."""
    parsed_page_url = urlparse(page_url)
    replacements: dict = {}
    soup = BeautifulSoup(page_code, 'html.parser')
    resource_urls = get_resource_urls(soup)
    progress_bar = Bar('Downloading resources', max=len(resource_urls))
    for url in resource_urls:
        parsed_url = urlparse(url)

        if not is_local_res(url, parsed_url.netloc, parsed_page_url.netloc):
            progress_bar.next()
            continue

        resource_link = urljoin(page_url, url)

        response = get_response(resource_link)

        resource_name = form_resource_name(resource_link)

        resource_file = get_resource_file(
            save_directory,
            resource_dir,
            resource_name,
        )

        if response and resource_file:
            save_resource(
                resource_file,
                response,
                replacements,
                resource_name,
                url,
            )
        progress_bar.next()
    if replacements:
        page_code = replace_links(soup, resource_dir, replacements)
    return page_code
