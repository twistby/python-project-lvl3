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
