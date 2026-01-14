"""This module contains the constants and enums used for pagination and sorting."""

from enum import Enum

DEFAULT_PAGE_NUMBER = 1
"""Pagination constants. Default page number is 1"""
DEFAULT_PAGE_SIZE = 10
"""Pagination constants. Default page size is 10"""
DEFAULT_CARD_PAGE_SIZE = 12
"""Pagination constants. Default card page size is 12"""
MAX_PAGE_SIZE = 1000
"""Pagination constants. Maximum page size is 100"""
MAX_LIMIT = 1000
"""Maximum limit for the list without pagination. Maximum limit is 1000"""


class SortDirection(str, Enum):
    """Sort direction enum."""

    ASC = "asc"
    DESC = "desc"
