"""Smoke tests for onnx_card."""

import pytest
from onnx_card import __version__
from onnx_card.core import ONNXCard


def test_version():
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_onnx_card_initialization():
    """Test that ONNXCard can be initialized."""
    card = ONNXCard()
    assert card is not None

