# -*- coding: utf-8 -*-
"""Test of the rhinopic functions.

Those tests are patching
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import os
import sys

from rhinopics.rhinobuilder import RhinoBuilder
from rhinopics.rhinopic import Rhinopic


class TestRhinopic(unittest.TestCase):
    """
    Unittest of rhinopic functions.
    """

    BASE_PATH = Path("tests/fixtures/")
    IMGA_NAME = Path("imgA.JPG")
    IMGB_NAME = Path("imgB.jpg")

    def setUp(self):
        # Create a temporary directory.
        self.test_dir = Path(tempfile.mkdtemp())
        print(self.test_dir)

        # Copy the fixtures folder.
        shutil.copytree(self.BASE_PATH, self.test_dir, dirs_exist_ok=True)

    def tearDown(self):
        """Reset the counter after each test."""
        Rhinopic.counter = 1

        shutil.rmtree(self.test_dir)

    def test_rename_pic_default(self):
        """
        Test the renaming of the files with default parameters.

        - Set the extension to lowercase.
        - Don't do a backup of the file.
        - Keyword is the parent directory.
        """
        n_digits = 1
        keyword = str(os.path.basename(os.getcwd()))
        backup = False
        lowercase = True

        test_cases = [
            (
                self.test_dir / self.IMGA_NAME,
                self.test_dir / f"{keyword}_20191224_1.jpg",
            ),
            (
                self.test_dir / self.IMGB_NAME,
                self.test_dir / f"{keyword}_NoDateFound_2.jpg",
            ),
        ]
        builder = RhinoBuilder(n_digits, keyword, backup, lowercase)

        for old_name, new_name in test_cases:
            with self.subTest(old_name=old_name, new_name=new_name):
                rhino = builder.factory(old_name)
                rhino.rename()

                # Since backup=False, old path should not exist.
                assert os.path.exists(old_name) is False
                assert os.path.exists(new_name) is True

    def test_rename_pic_keyword_multiple_digits(self):
        """
        Test the renaming of the files.
        """
        n_digits = 4
        keyword = "testA"
        backup = False
        lowercase = False

        test_cases = [
            (
                self.test_dir / self.IMGA_NAME,
                self.test_dir / f"{keyword}_20191224_0001.JPG",
            ),
            (
                self.test_dir / self.IMGB_NAME,
                self.test_dir / f"{keyword}_NoDateFound_0002.jpg",
            ),
        ]
        builder = RhinoBuilder(n_digits, keyword, backup, lowercase)

        for old_name, new_name in test_cases:
            with self.subTest(old_name=old_name, new_name=new_name):
                rhino = builder.factory(old_name)
                rhino.rename()

                # Since backup=False, old path should not exist.
                assert os.path.exists(old_name) is False
                assert os.path.exists(new_name) is True

    def test_rename_pic_backup(self):
        """
        Test the renaming of the files.

        Test with a backup (copy) of the file.
        """
        n_digits = 1
        keyword = "test_with_backup"
        backup = True
        lowercase = True

        test_cases = [
            (
                self.test_dir / self.IMGA_NAME,
                self.test_dir / f"{keyword}_20191224_1.jpg",
            ),
            (
                self.test_dir / self.IMGB_NAME,
                self.test_dir / f"{keyword}_NoDateFound_2.jpg",
            ),
        ]
        builder = RhinoBuilder(n_digits, keyword, backup, lowercase)

        for old_name, new_name in test_cases:
            with self.subTest(old_name=old_name, new_name=new_name):
                rhino = builder.factory(old_name)
                rhino.rename()

                # Since backup=True, old path should exist.
                assert os.path.exists(old_name) is True
                assert os.path.exists(new_name) is True


if __name__ == "__main__":
    from pkg_resources import load_entry_point

    sys.exit(load_entry_point("pytest", "console_scripts", "py.test")())
