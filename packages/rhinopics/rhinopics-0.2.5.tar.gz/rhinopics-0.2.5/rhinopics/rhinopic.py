# -*- coding: utf-8 -*-
"""rhinopics class.

This class contains functions to rename pictures.
"""

from datetime import datetime
from typing import ClassVar

import exifread

from .rhinofile import Rhinofile


class Rhinopic(Rhinofile):
    """Class to rename picture viles.

    Supported types are defined in the `Rhinofile` class.
    """

    counter = 1

    # Possible fields in the exif data.
    TAGS_DATE: ClassVar[set] = {
        "EXIF DateTimeOriginal",
        "EXIF DateTimeDigitized",
        "EXIF DateTime",
    }

    def get_date(self, full: bool = False) -> str:
        """
        Retrieve the date of a picture.

        The date is retrieved using the `exifread` package.
        Possible tags must be parsed manually until one is found.

        Parameters
        ----------
        full : bool, default False
            If full, return the seconds, otherwise, only the day.

        Returns
        -------
        str
            Date as a string in the following format: %Y%m%d.
            If date is not found, return 'NoDateFound'.
        """
        with self.path.open(mode="rb") as fid:
            tags_read = exifread.process_file(fid)

            for tag in self.TAGS_DATE:
                if tag in tags_read.keys():
                    date = datetime.strptime(str(tags_read[tag]), "%Y:%m:%d %H:%M:%S")
                    if not full:
                        return date.strftime("%Y%m%d")
                    return date.strftime("%Y%m%d %H%M%S")

        return "NoDateFound"

    def rename(self):
        """
        Rename the picture file.

        Picture file is renamed with the given keyword and the date of the video.

        The counter is shared between instances.
        """
        date = self.get_date()
        new_name = (
            f"{self.keyword}_{date}_{str(Rhinopic.counter).rjust(self.nb_digits, '0')}"
            f"{self.path.suffix.lower() if self.lowercase else self.path.suffix}"
        )
        new_path = self.path.with_name(new_name)
        if not new_path.exists():
            if self.backup:
                with new_path.open(mode="xb") as fid:
                    fid.write(self.path.read_bytes())
                self.logger.info(f"Copying {self.path} to {new_path}.")
                print(f"Copying {self.path} to {new_path}.")
            else:
                self.path.replace(new_path)
                self.logger.info(f"Renaming {self.path} to {new_path}.")
                print(f"Renaming {self.path} to {new_path}.")
            Rhinopic.counter += 1
        else:
            print(f"Path {new_path} already exists.")

    def __str__(self):
        """String representation of class."""
        return f"Rhinopic: {self.path}"
