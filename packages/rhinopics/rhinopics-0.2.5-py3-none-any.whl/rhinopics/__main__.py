# -*- coding: utf-8 -*-
"""Entry point of the rhinopics cli."""

import datetime
import os
import pathlib

import click
import click_pathlib
from tqdm import tqdm

from .rhinobuilder import RhinoBuilder


@click.command()
@click.argument("keyword", type=str, default=str(os.path.basename(os.getcwd())))
@click.option(
    "--directory",
    "-d",
    default="./",
    show_default=True,
    type=click_pathlib.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Directory containing the pictures to rename.",
)
@click.option(
    "--backup",
    "-b",
    is_flag=True,
    show_default=True,
    help="Create copies instead of renaming the files.",
)
@click.option(
    "--lowercase",
    "-l",
    is_flag=True,
    default=True,
    show_default=True,
    help="Modify the extension to lowercase.",
)
def main(keyword: str, directory: pathlib.PosixPath, backup: bool, lowercase: bool):
    """Rename all pictures in a directory with a common keyword.

    The date from the metadata of the pictures is retrieved and concanated
    to the keyword, followed by a counter to distinguish pictures taken the same day.

    Parameters
    ----------
    keyword : str
        Common keyword to use when renaming the pictures.
        The default value is the name of the current folder.
    directory : str, default './'
        Directory containing the pictures to rename, default is the current directory.
    backup : bool, default False
        If flag is present, copy the pictures instead of renaming them.

    Examples
    --------
    $ rhinopics mykeyword
    -> mykeyword_20190621_001
    """
    paths = list(directory.glob("*"))
    nb_digits = len(str(len(paths)))
    builder = RhinoBuilder(nb_digits, keyword, backup, lowercase)

    # First pass to get the dates.
    paths_with_dates = []

    try:
        for path in paths:
            date = builder.factory(path).get_date(full=True)
            if date == "NoDateFound":
                date = datetime.datetime.max
            paths_with_dates.append((path, date))
    except AttributeError:
        print(f"Cannot handle file: {path}.")

    paths_sorted = [i[0] for i in sorted(paths_with_dates, key=lambda x: x[1])]

    with tqdm(total=len(paths_sorted)) as pbar:
        for path in paths_sorted:
            rhino = builder.factory(path)
            if rhino is not None:
                rhino.rename()
            pbar.update()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
