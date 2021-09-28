"""Page resources loader module."""
import logging
import os
import re
from typing import Optional
from urllib.parse import ParseResult, urlparse

import requests
from bs4 import BeautifulSoup  # type: ignore

IMAGE_TAG = 'img'
LINK_TAG = 'link'
SCRIPT_TAG = 'script'
SRC_ATTR = 'src'
HREF_ATTR = 'href'
TAGS_ATTR = {  # noqa: WPS407
    IMAGE_TAG: SRC_ATTR,
    LINK_TAG: HREF_ATTR,
    SCRIPT_TAG: SRC_ATTR,
}
FILE_RE_PATTERN = '[^0-9a-zA-Z.]+'  # noqa: W605
LINK_RE_PATTERN = '[^0-9a-zA-Z]+'  # noqa: W605


def get_resource_link(parsed_page: ParseResult, path: str) -> str:
    """Get image link."""
    if path[0] == '.':
        path = path[1:]
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


def form_resource_name(  # noqa: C901
    res_path: Optional[str],
    res_host: Optional[str] = '',
) -> str:
    """Form file name from link."""
    resource_name = ''
    if res_host and res_path:
        host_part = re.sub(LINK_RE_PATTERN, '-', res_host)  # noqa: W605
        if '/' not in res_path:
            new_path = '/{p}'.format(p=res_path)
        else:
            new_path = res_path
        *path, file_name = new_path.split('/')
        path_part = re.sub(LINK_RE_PATTERN, '-', ''.join(path))
        file_part = re.sub(FILE_RE_PATTERN, '-', file_name)
        resource_name = '{h}{pp}-{fp}'.format(
            h=host_part,
            pp=path_part,
            fp=file_part,
        )
    return resource_name


def get_resource_pathes(page):
    """Collect pathes of resources."""
    with open(page) as local_page:
        soup = BeautifulSoup(local_page, 'html.parser')
    resource_pathes = {tag[SRC_ATTR] for tag in soup.findAll(name=IMAGE_TAG)}
    link_pathes = {tag[HREF_ATTR] for tag in soup.findAll(name=LINK_TAG)}
    script_pathes = set()
    script_tags = soup.findAll(name=SCRIPT_TAG)
    for tag in script_tags:
        if tag.has_attr(SRC_ATTR):
            script_pathes.add(tag[SRC_ATTR])
    return resource_pathes.union(link_pathes.union(script_pathes))


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


def replace_links(page: str, resource_dir: str, replace_data: dict) -> None:
    """Replace links to images in page."""
    with open(page) as local_page:
        soup = BeautifulSoup(local_page, 'html.parser')
    for tag_name, attr_name in TAGS_ATTR.items():
        resource_tags = soup.findAll(name=tag_name)
        change_tags(resource_tags, attr_name, replace_data, resource_dir)
    with open(page, 'w') as new_page:
        new_page.write(soup.prettify())


def download_resurces(  # noqa: C901, WPS210, WPS213
    local_page_path: str,
    page_adress: str,
    save_directory: str,
    resource_dir: str,
    agent_header: dict,
) -> None:
    """Download web-page resources."""
    parsed_page = urlparse(page_adress)
    replacements = {}
    resource_pathes = get_resource_pathes(local_page_path)
    for path in resource_pathes:
        parsed_path = urlparse(path)
        if not path:
            continue
        if parsed_path.netloc and parsed_path.netloc != parsed_page.netloc:
            continue

        if parsed_path.scheme == '':
            resource_name = form_resource_name(
                parsed_path.path,
                parsed_page.hostname,
            )
            resource_link = get_resource_link(parsed_page, path)
        elif parsed_path.hostname == parsed_page.hostname:
            resource_name = form_resource_name(
                parsed_path.path,
                parsed_path.hostname,
            )
            resource_link = path
        else:
            logging.debug('Something wrong with resource: {r}'.format(r=path))
            continue
        res_content = get_resource(resource_link, agent_header)
        with open(
            os.path.join(save_directory, resource_dir, resource_name),
            'wb',
        ) as resource_file:
            resource_file.write(res_content)
            resource_file.close()
        replacements[path] = resource_name
    if replacements:
        replace_links(local_page_path, resource_dir, replacements)


def get_resource(resource_adress: str, header: dict) -> bytes:
    """Try to get resource content."""
    response = requests.get(url=resource_adress, headers=header)
    if response.ok:
        return response.content
    raise ConnectionError("Can't get resource {r}. {err}".format(
        r=resource_adress,
        err=response.status_code,
    ),
    )
