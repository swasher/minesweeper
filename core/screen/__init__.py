"""Инициализация и экспорт screen-специфичных компонентов"""
import assets
from config import config

asset_screen = config.asset
assets.init(asset_screen)

from .screen_matrix import ScreenMatrix
from .find_board import find_board

__all__ = ['ScreenMatrix', 'find_board']