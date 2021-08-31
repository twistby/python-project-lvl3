"""Test module."""
import os
import tempfile

import pytest

from page_loader.page_loader import DEFAULT_SAVE_DIR, download, form_file_name


def test_form_file_name():
    """Test file name formation."""
    link = ''
    file_name = ''
    assert form_file_name(link) == file_name
    link = 'https://ru.hexlet.io/courses'
    file_name = 'ru-hexlet-io-courses.html'
    assert form_file_name(link) == file_name
    link = 'http://hexlet.io/course'
    file_name = 'hexlet-io-course.html'
    assert form_file_name(link) == file_name


def test_download():
    """Download test."""
    link = 'https://ru.hexlet.io/courses'
    file_name = 'ru-hexlet-io-courses.html'

    download(link)
    assert os.path.exists(os.path.join(DEFAULT_SAVE_DIR, file_name)) is True

    with tempfile.TemporaryDirectory() as tmpdirname:
        full_path = download(link, tmpdirname)
        assert os.path.join(tmpdirname, file_name) == full_path
        assert os.path.exists(os.path.join(tmpdirname, file_name)) is True


def test_download_to_wrong_dir():
    """Download to wrong directory test."""
    link = 'https://ru.hexlet.io/courses'
    with pytest.raises(ValueError):
        download(link, '/wrong_dir')
