"""Shared pytest fixtures for headless Skybound tests.

Sets dummy SDL drivers *before* pygame ever touches a display or audio
device, so the whole suite runs in CI / over SSH with no window or sound card.
"""

import os

# Must be set before pygame initialises any subsystem.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg  # noqa: E402  (import after env setup is intentional)
import pytest


@pytest.fixture(scope="session", autouse=True)
def _pygame_session():
    """Initialise pygame once with an off-screen display for the whole suite."""
    pg.init()
    try:
        pg.mixer.init()
    except pg.error:
        # No audio device available even with the dummy driver — fine for tests.
        pass
    pg.display.set_mode((480, 600))
    yield
    pg.quit()
