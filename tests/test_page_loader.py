"""Test module."""
from page_loader.page_loader import download


def test_download():
    """Download test."""
    assert download('1', '2') == ''
