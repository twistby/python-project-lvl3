"""Test page download module."""
import os
import tempfile

import pytest
from bs4 import BeautifulSoup as bs  # noqa: N813
from requests_mock import ANY as RM_ANY

from page_loader.page_loader import download


def get_path(file_name: str) -> str:
    """Get abs path to fixture file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'fixtures', file_name)


def read(file_path: str) -> str:
    """Read the file."""
    with open(file_path, 'r') as f_file:
        f_result = f_file.read()
    return f_result


def test_download_to_wrong_dir(requests_mock):
    """Test download to wrong directory."""
    link = 'https://ru.hexlet.io/courses'
    directory = '/vart/tmp/1'
    requests_mock.get(link, text='test')
    with pytest.raises(ValueError):
        download(link, directory)


@pytest.mark.parametrize(
    'page_url, file_name',
    [
        (
            'http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm',  # noqa: E501
            'help-websiteos-com-websiteos-example-of-a-simple-html-page-htm.html',  # noqa: E501
        ),
    ],
)
def test_download_to_default_dir(requests_mock, page_url, file_name):
    """Test download to default directory."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        requests_mock.get(page_url, text='test')
        download(page_url)
        assert os.path.exists(os.path.join(tmpdirname, file_name)) is True


@pytest.mark.parametrize(
    'page_url, expected_file',
    [
        (
            'http://visiions-of-you.com/inspiredby/samneill/wp/',
            'Sam_Neill_Web.html',
        ),
    ],
)
def test_download(requests_mock, page_url, expected_file):
    """Test download function."""
    requests_mock.get(page_url, text=read(get_path(expected_file)))

    with tempfile.TemporaryDirectory() as tmpdirname:
        full_path = download(page_url, tmpdirname)
        assert os.path.exists(full_path) is True
        assert os.path.isfile(full_path) is True
        assert bs(
            read(full_path),
            features='html.parser',
        ).prettify() == bs(
            read(get_path(expected_file)),
            features='html.parser',
        ).prettify()


@pytest.mark.parametrize(
    'page_url, page_content, resources_dir, expected_files',
    [
        (
            'http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm',  # noqa: E501
            'Simple_HTML_page.html',
            'help-websiteos-com-websiteos-example-of-a-simple-html-page-htm_files',  # noqa: E501
            'resources_list.txt',
        ),
    ],
)
def test_download_resources(
    requests_mock,
    page_url,
    page_content,
    resources_dir,
    expected_files,
):
    """Test download resources."""
    requests_mock.get(RM_ANY, text='test content')
    requests_mock.get(page_url, text=read(get_path(page_content)))
    with tempfile.TemporaryDirectory() as tmpdirname:
        download(page_url, tmpdirname)
        resources_dir_path = os.path.join(tmpdirname, resources_dir)
        assert os.path.exists(resources_dir_path) is True
        saved_files = os.listdir(resources_dir_path)
        excepted_files_list = read(get_path(expected_files)).split()
        assert sorted(saved_files) == sorted(excepted_files_list)
