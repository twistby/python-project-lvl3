"""Page resources loader module."""
import logging
import os
import re
from typing import Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup  # type: ignore
from fake_useragent import UserAgent  # type: ignore
from progress.bar import Bar  # type: ignore

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


def form_resource_name(
    res_path: Optional[str],
    res_host: Optional[str] = '',
) -> str:
    """Form file name from link."""
    resource_name = ''
    if res_host and res_path:
        host_part = re.sub(LINK_RE_PATTERN, '-', res_host)
        if '/' not in res_path:
            new_path = '/{p}'.format(p=res_path)
        else:
            new_path = res_path

        file_extention_obj = re.search(
            FILE_EXT_RE_PATTERN,
            new_path,
            flags=re.IGNORECASE,
        )
        if file_extention_obj is None:
            file_extention = '.html'
        else:
            file_extention = file_extention_obj.group(0)

        new_path = new_path.replace(file_extention, '')

        path_part = re.sub(LINK_RE_PATTERN, '-', new_path)
        if file_extention is None:
            file_extention = '.html'
        resource_name = '{h}{pp}{fe}'.format(
            h=host_part,
            pp=path_part,
            fe=file_extention,
        )
    return resource_name


def get_resource_paths(soup: BeautifulSoup) -> set:
    """Collect paths of resources."""
    resource_paths: Set[str] = set()
    for tg, atr in TAGS_ATTR.items():
        resource_paths = resource_paths.union(
            {tag[atr] for tag in soup.findAll(name=tg) if tag.has_attr(atr)},
        )
    return resource_paths


def change_tags(
    tags: set,
    atribute: str,
    replace_data: dict,
    resource_dir: str,
) -> None:
    """Change tags attributs."""
    for tag in tags:
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
    for tag_name, attr_name in TAGS_ATTR.items():
        resource_tags = soup.findAll(name=tag_name)
        change_tags(resource_tags, attr_name, replace_data, resource_dir)
    return soup.prettify()


def download_resurces(
    page_code: str,
    page_address: str,
    save_directory: str,
    resource_dir: str,
) -> str:
    """Download web-page resources."""
    parsed_page = urlparse(page_address)
    replacements = {}
    soup = BeautifulSoup(page_code, 'html.parser')
    resource_paths = get_resource_paths(soup)
    progress_bar = Bar('Downloading resources', max=len(resource_paths))
    for path in resource_paths:
        parsed_path = urlparse(path)

        if parsed_path.netloc and parsed_path.netloc != parsed_page.netloc:
            progress_bar.next()
            continue

        resource_link = urljoin(page_address, path)

        try:
            response = requests.get(
                url=resource_link,
                headers=DEFAULT_HEADER,
                stream=True,
            )
            response.raise_for_status()
        except Exception as err:
            logging.debug(
                'Something wrong with resource: {r}. {err}'.format(
                    r=resource_link,
                    err=err,
                ),
            )
            continue

        resource_name = form_resource_name(
            parsed_path.path,
            parsed_page.hostname,
        )

        with open(
            os.path.join(save_directory, resource_dir, resource_name),
            'wb',
        ) as resource_file:
            for chunk in response.iter_content(chunk_size=1024):
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
        progress_bar.next()
    if replacements:
        page_code = replace_links(soup, resource_dir, replacements)
    return page_code
