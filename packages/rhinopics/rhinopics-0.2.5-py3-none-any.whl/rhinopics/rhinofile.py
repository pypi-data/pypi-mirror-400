# -*- coding: utf-8 -*-
"""rhinofile interface."""

import abc
import logging
import pathlib


class Rhinofile(abc.ABC):
    """
    Rhinofile interface.

    All classes that inherite from `Rhinofile` must have those method.

    Attributes are the same as the `RhinoBuilder` factory class in addition
    to the path of the file to proces.
    """

    def __init__(
        self,
        path: pathlib.PosixPath,
        nb_digits: int,
        keyword: str,
        backup: bool,
        lowercase: bool,
    ):
        self.logger = logging.getLogger(__name__)
        self.nb_digits = nb_digits
        self.keyword = keyword
        self.backup = backup
        self.lowercase = lowercase
        self.path = path

    @abc.abstractmethod
    def get_date(self, full: bool = False) -> str:
        """
        Get the date of a file.

        Type of the file depends of the subclass.
        """

    @abc.abstractmethod
    def rename(self):
        """
        Rename a file.

        Type of the file depends of the subclass.
        """
