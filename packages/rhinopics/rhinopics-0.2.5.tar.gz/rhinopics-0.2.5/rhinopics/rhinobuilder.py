# -*- coding: utf-8 -*-
"""rhinobuilder class."""

import logging
from typing import ClassVar

from .rhinopic import Rhinopic
from .rhinovid import Rhinovid


class RhinoBuilder:
    """Factory class to create `Rhinopic` or `Rhinovid` objects."""

    VIDEO_EXTS: ClassVar[set] = {".avi", ".AVI", ".mov", ".MOV"}
    IMG_EXTS: ClassVar[set] = {".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG"}

    def __init__(self, nb_digits: int, keyword: str, backup: bool, lowercase: bool):
        self.logger = logging.getLogger(__name__)
        self.nb_digits = nb_digits
        self.keyword = keyword
        self.backup = backup
        self.lowercase = lowercase

    def factory(self, path):
        """
        Factory method to create the object.

        Depending on the type of file, the appropriate object is created.
        """
        if path.suffix in self.IMG_EXTS:
            return Rhinopic(
                path, self.nb_digits, self.keyword, self.backup, self.lowercase
            )
        if path.suffix in self.VIDEO_EXTS:
            return Rhinovid(
                path, self.nb_digits, self.keyword, self.backup, self.lowercase
            )
        self.logger.info(f"Extension {path.suffix} not supported")
        return None
