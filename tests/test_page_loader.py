"""Test module."""
import os
import tempfile

import pytest

from page_loader.page_loader import DEFAULT_SAVE_DIR, download


def test_download():
    """Test download function."""
    link = 'http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm'  # noqa: E501
    file_name = 'help-websiteos-com-websiteos-example-of-a-simple-html-page-htm.html'  # noqa: E501
    dir_name = DEFAULT_SAVE_DIR

    download(link)
    assert os.path.exists(os.path.join(DEFAULT_SAVE_DIR, file_name)) is True

    with tempfile.TemporaryDirectory() as tmpdirname:
        full_path = download(link, tmpdirname)
        assert os.path.join(tmpdirname, file_name) == full_path
        assert os.path.exists(os.path.join(tmpdirname, file_name)) is True
        assert os.path.exists(os.path.join(tmpdirname, dir_name)) is True
        assert os.path.isdir(os.path.join(tmpdirname, dir_name)) is True


def test_download_to_wrong_dir():
    """Test download to wrong directory."""
    link = 'https://ru.hexlet.io/courses'
    directory = '/vart/tmp/1'
    with pytest.raises(ValueError):
        download(link, directory)


def test_image_download():
    """Tset downloading images of page."""
    link = 'http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm'  # noqa: E501
    dir_name = 'help-websiteos-com-websiteos-example-of-a-simple-html-page-htm_files'  # noqa: E501
    img_name = 'help-websiteos-com-htmlpage.jpg'
    with tempfile.TemporaryDirectory() as tmpdirname:
        download(link, tmpdirname)
        assert os.path.exists(os.path.join(tmpdirname, dir_name)) is True
        assert os.path.exists(os.path.join(tmpdirname, dir_name, img_name)) is True  # noqa: E501


def get_path(file_name: str) -> str:
    """Get abs path to fixture file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'fixtures', file_name)


def read(file_path: str) -> str:
    """Read the file."""
    with open(file_path, 'r') as f_file:
        f_result = f_file.read()
    return f_result


def test_replace_images():
    """Test replased image source."""
    true_file = get_path('replace_images.txt')
    expected = read(true_file)
    link = 'http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm'  # noqa: E501
    file_name = 'help-websiteos-com-websiteos-example-of-a-simple-html-page-htm.html'  # noqa: E501
    with tempfile.TemporaryDirectory() as tmpdirname:
        download(link, tmpdirname)
        result_file = read(os.path.join(tmpdirname, file_name))
        assert expected == result_file
