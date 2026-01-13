import os
from glob import glob
from typing import (
    Callable,
    List
)
from .collections import make_list


def get_dir_files(
        dir: str | List[str],
        ext: str | List[str] = "*",
        recursive: bool = True,
        key: Callable | None = None
) -> List[str]:
    """Returns a `list` with all the files inside folder with extension `ext`.
    It supports a recursive search and searching in more than one root folder
    at a time if `recursive=True` and `dir` is a `list` of `str`,
    respectively.

    Args:
        dir (str | List[str]): Folder(s) to be searched.
        ext (str | Tuple[str]): File extensions to be considered. Accepts `.*`
            as a wild card.
        recursive (bool): If `True`, the search inside each folder will be
            recursive.
        key (Callable | None): Key function to sort the results. If it is not
            provided, files will be sorted alphabetically.

    Returns:
        `list` of `str` with the path to each retrieved file.

    Raises:
        FileNotFoundError: If one of the folder(s) cannot be found.
    """
    dir = make_list(dir)
    ext = make_list(ext)

    # Expand user and vars
    for idx, dir_ in enumerate(dir):
        dir[idx] = dir_

    # Check dirs exist before fetching content
    for dir_ in dir:
        if not os.path.isdir(dir_):
            raise FileNotFoundError(f"Folder not found: '{dir_}'")

    all_files = []

    # Search dirs
    for dir_ in dir:
        for ext_ in ext:
            if recursive:
                all_files.extend(
                    list(
                        glob(
                            os.path.join(dir_, "**", f"*{ext_}"),
                            recursive=True
                        )
                    )
                )
            else:
                all_files.extend(list(glob(os.path.join(dir_, f"*{ext_}"))))
    
    # Filter out folders with file-like names (e.g. ending in .wav extension)
    flagged_files = []

    for file in all_files:
        if not os.path.isfile(file):
            flagged_files.append(file)
    
    for flagged_file in flagged_files:
        all_files.remove(flagged_file)

    return sorted(all_files, key=key)
