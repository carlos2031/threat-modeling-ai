"""Tests for app.main."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from app.main import lifespan


def test_lifespan():
    """lifespan creates tables on startup and disposes engine on shutdown."""
    mock_app = MagicMock()
    mock_engine = MagicMock()
    mock_create_all = MagicMock()

    async def run():
        with patch("app.main.engine", mock_engine):
            with patch("app.main.Base.metadata.create_all", mock_create_all):
                async with lifespan(mock_app):
                    pass
        mock_create_all.assert_called_once_with(bind=mock_engine)
        mock_engine.dispose.assert_called_once()

    asyncio.run(run())
