"""Инициализация и экспорт TK-специфичных компонентов"""
import assets
assets.init('asset_tk')

from .tk_matrix import TkMatrix

__all__ = ['TkMatrix']