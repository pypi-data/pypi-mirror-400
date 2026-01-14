"""
Main functions to read git patches
"""

import re
import os
from loguru import logger
import json
from pathlib import Path
from typing import Tuple, List


def find_patches(folderpath: str, verbose: bool = False) -> dict:
    """Parse patches from :
    ```
    From abcdefghijklmnopqrstuvwxyz Mon Sep 17 00:00:00 2001
    From: toto <toto@email.fr>
    Date: Fri, 25 Jul 2025 13:28:26 +0200
    Subject: [PATCH 1/N] Hello world


    src/a.py     | 18 ++++++++++++++----
    src/b.py     | 17 +++++++++++------
    src/c.py     |  6 ++++++
    3 files changed, 31 insertions(+), 10 deletions(-)
    ```

    to

    ```
    {
        "a.py": {"changes": 18, "insertions": 10, "deletions": 8},
        "b.py": {"changes": 17, "insertions": 12, "deletions": 5},
        "c.py": {"changes": 6, "insertions": 6, "deletions": 0}
    }
    ```

       Args:
           path (str): Patches folder path
           verbose (bool, optional): Verbose mode. Defaults to False.

       Returns:
           dict: Patches summary in a form of a dict
    """
    real_patches = [
        files for files in os.listdir(folderpath) if files.endswith(".patch")
    ]
    patches = {}

    for idf, fpatches in enumerate(real_patches):
        if verbose:  # pragma: no cover
            logger.debug(f"Reading {fpatches} ({idf+1}/{len(real_patches)})")

        file = Path(folderpath) / fpatches
        with open(file, "r") as f:
            ptch = f.read()

        diffstat, patch, summary = _split_file(ptch)

        delta = _count_line_delta(patch)
        changes = _get_nb_changes(diffstat)
        total = _get_total_insert_delet_patch(summary)
        patch_diff = _set_patches(changes, delta, total, verbose)

        # add in general path
        for path, delta in patch_diff.items():
            if path in patches.keys():
                for k, v in delta.items():
                    patches[path][k] += v
            else:
                patches[path] = delta

    return patches


def _split_file(ptch: str) -> Tuple[str, str, str]:
    """
    Split patch file in 3 parts:

    * diffstat :

    ```
    src/folder/myfile.py   | 5 -----
    src/folder/other.py    | 7 +++++
    ```

    * summary :

    ```
    2 files changed, 7 insertions(+), 5 deletions(-)
    ```

    * core diff (`diff --git`)

    ```
    diff --git a/src/folder/myfile.py  b/src/folder/myfile.py
    index a430cbdd1..c53b2f9d1 304593
    --- a/src/folder/myfile.py
    +++ b/src/folder/myfile.py
    @@ -174,11 +174,6
    ```

    Args:
        ptch (str): Raw patch text

    Returns:
        Tuple[str, str, str]: diffstat part / core diff part / summary part
    """
    summary_line_re = re.compile(r"\d+ file[s]? changed, [\s\S]*?\n", re.MULTILINE)
    m = summary_line_re.search(ptch)
    assert (
        m
    ), "Can't find 'N files changed, M insertions(+), X deletions(-)'-type line in file."
    summary = ptch[m.start() : m.end()]
    diffstat = ptch[: m.start()].strip()
    patch = ptch[m.end() :].strip()
    return diffstat, patch, summary


def _count_line_delta(ptch: str) -> dict:
    """
    Count delta between before/after lines number for each file.

    For example:

    ```
    diff --git a/src/folder/myfile.py  b/src/folder/myfile.py
    index a430cbdd1..c53b2f9d1 304593
    --- a/src/folder/myfile.py
    +++ b/src/folder/myfile.py
    @@ -174,11 +174,6
    ```

    -> Line shown in the original file : 11.
    -> Lines shown in the new file: 6.
    -> Line delta : 11 - 6 = -5
    -> There are 5 more deletions than insertions

    Args:
        ptch (str): Raw diff text

    Returns:
        dict: Line delta for each file - {"path0": N, "path1": M, ...}
    """
    file_path = re.compile(
        r"diff --git a/(.+?) [\s\S]*?",
        re.MULTILINE,
    )
    file_diff = re.compile(
        r"^@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@",
        re.MULTILINE,
    )
    path = None
    delta = {}
    for line in ptch.splitlines():
        mp = file_path.match(line)
        md = file_diff.match(line)
        # find path = line starting with
        if mp:
            path = mp.group(1).strip()
            delta[path] = 0
            continue
        if md:
            assert (
                path
            ), f"Find a line change but couldn't find the name of the function related before. Stops at '{line}'"
            delta[path] += int(md.group(2)) - int(md.group(1))
    return delta


def _get_total_insert_delet_patch(line: str) -> dict:
    """Get total number of insertions/deletions

    Args:
        line (str): Summary line in diffstat :
        "2 files changed, 7 insertions(+), 5 deletions(-)"

    Returns:
        dict: {
        "insertions" : total_nb_of_insertions,
        "deletions" : total_nb_of_deletions
        }
    """
    search_file = re.search(r"(\d+) file", line)
    assert search_file, f"Can't parse the number of files in '{line}'."
    nb_file = int(search_file.group(1))

    search_file = re.search(r"(\d+) insertion", line)
    insert = int(search_file.group(1)) if search_file else 0

    search_delet = re.search(r"(\d+) deletion", line)
    delet = int(search_delet.group(1)) if search_delet else 0

    return {"insertions": insert, "deletions": delet, "files": nb_file}


def _set_patches(changes: dict, delta: dict, total: dict, verbose: bool = False) -> dict:
    """Build final patch data for a patch

    Args:
        changes (dict): Total number of changes per file
        delta (dict): Line delta per file
        total (dict): Total number of insertions/deletions
        verbose (bool): Verbose mode.

    Returns:
        dict: Changes, insertions and deletions number per file
        {
        "file0": {"changes": 10, "insertions": 5, "deletions": 5},
        "file1": {"changes": 8, "insertions": 2, "deletions": 6},
        ...
        }
    """
    patches = {}
    for cpath in changes.keys():
        path = [pth for pth in delta.keys() if cpath in pth][0]
        patches[path] = {"changes": changes[cpath]}
        insert, delt = _calc_insert_del(delta[path], changes[cpath])
        patches[path]["insertions"] = insert
        patches[path]["deletions"] = delt
        if verbose:  # pragma: no cover
            logger.debug(f"Find {changes[cpath]} modification(s) in {cpath} [{insert} insertion(s) | {delt} deletion(s)]")

    # direct assertions
    count_insert = sum([patches[path]["insertions"] for path in patches.keys()])
    assert (
        total["insertions"] == count_insert
    ), f"Suppose to find {total['insertions']} insertion(s) but find {count_insert}."
    count_delet = sum([patches[path]["deletions"] for path in patches.keys()])
    assert (
        total["deletions"] == count_delet
    ), f"Suppose to find {total['deletions']} deletion(s) but find {count_delet}."
    nb_files = len(list(patches.keys()))
    assert (
        total["files"] == nb_files
    ), f"Suppose to find {total['files']} file(s) but find {nb_files}."

    return patches


def _get_nb_changes(ptch: str) -> dict:
    """Traverse the diff stat part of a patch to retrieve the number of changes
    per file:

    ```
    src/folder/myfile.py   | 15 --++
    src/folder/other.py    | 7 +++++
    2 files changed, 10 insertions(+), 5 deletions(-)
    ```

    gives :

    {
        "src/folder/myfile.py": 15,
        "src/folder/other.py ": 7,
    }

    Args:
        ptch (str): Raw patch text (not splitted)
        diff (dict): Line delta (see _count_line_delta())

    Returns:
        dict: Total number of changes per file
    """

    changes = {}
    file_stat = re.compile(r"^\s*([^|]+)\s*\|\s*(\d+)\s+[+-]+$")  # diff stat
    for line in ptch.splitlines():
        m = file_stat.match(line)
        if m:
            path = m.group(1).strip()
            if "..." in path.split("/"):
                path = "/".join(path.split("/")[1:])
            nb_changes = int(m.group(2))
            # add nb_changes to patches
            changes[path] = nb_changes

    return changes


def _calc_insert_del(delta: int, nb_changes: int):
    """Calculate the number of insertions and deletions in a file.

    From `diff --git`, we have the line delta:

    ```
    diff --git a/src/folder/myfile.py  b/src/folder/myfile.py
    index a430cbdd1..c53b2f9d1 304593
    --- a/src/folder/myfile.py
    +++ b/src/folder/myfile.py
    @@ -174,11 +174,6
    ```

    -> Line shown in the original file : 11.
    -> Lines shown in the new file: 6.
    -> Line delta : 11 - 6 = -5
    -> There are 5 more deletions than insertions

    And from diffstat, we have the number of changes:

    ```
    src/folder/myfile.py   | 9 ----+
    ```

    -> Total changed lines: 9 (insertions + deletions)

    The remaining changes are balanced insertions/deletions:
    -> balanced = nb_changes - delta = 9 - 5 = 4
    Balanced changes are evenly split between insertions and deletions:
    -> insertions = balanced / 2 = 2
    -> deletions = balanced / 2 + delta = 2 + 5 = 7

    Total : 7 deletions and 2 insertions = 9 changes.

    Args:
        delta (int): Line delta
        nb_changes (int): Total change (insertions+deletions)

    Returns:
        Tuple[int,int]: Nb insertions/deletions
    """
    insert, delt = 0, 0
    if delta > 0:
        insert = abs(delta)
    else:
        delt = abs(delta)
    if nb_changes != abs(delta):
        assert nb_changes > abs(
            delta
        ), f"Line delta ({abs(delta)}) is higher than the number total of changes ({nb_changes})."
        add_to = int((nb_changes - abs(delta)) / 2)
        # TODO : test if it is an integer
        insert += add_to
        delt += add_to
    return insert, delt


def _build_struct_repo_patches(data: dict, patches: dict) -> dict:
    """[recursive] Build struct repo from git patches using struct repo data
    and patches info.

    Args:
        data (dict): data loaded from struct_repo
        patches (dict): Patches in a form of a dict : {"filepath0" : M, "filepath1": N, ...}

    Returns:
        (dict): Nested struct repo data adapted to git patches visualization.
        patches_tree = {
            "name": "hello",
            "path": "package:hello",
            "NLOC": 10,               # mandatory to compute circles's size
            "status": "changed",      # changed / unchanged
            "modifications": 20,      # insertions + deletions
            "children": [...],
        }
    """

    # order is important
    tree_patches = {
        "name": data["name"],
        "path": data["path"],
        "status": "Unchanged",
        "modifications": 0,
        "insertions": 0,
        "deletions": 0,
        "type": data["type"],
        "NLOC": data["NLOC"],
    }

    path = _find_in_path(data["path"], list(patches.keys()))
    if path:
        tree_patches["modifications"] = patches[path]["changes"]
        tree_patches["insertions"] = patches[path]["insertions"]
        tree_patches["deletions"] = patches[path]["deletions"]

    tree_patches["status"] = "Changed" if tree_patches["modifications"] else "Unchanged"

    children = data["children"]
    tree_patches["children"] = []
    if children:
        for child in children:
            child_struct = _build_struct_repo_patches(child, patches)
            tree_patches["children"].append(child_struct)
    return tree_patches

def _find_in_path(path:str, path_patches: List[str]) -> Tuple[str, None]:
    """Find path (from struct_repo) in list of modified paths (from git patches)

    The root of the path is not necessarily the same between struct_repo and git patches. e.g:
        -> path from patches = "src/utils/my_code.f90" (root is "my_package")
        -> path from struct_repo = "utils/my_code.f90" (root is "my_package/src")
    So find path equivalence by checking :
        1- if same filename (here "my_code.f90" == "my_code.f90" ?)  
        2- if path from struct_repo (shorter) is included in path from patches (here "utils/my_code.90" in "src/utils/my_code.f90" ?) 

    Args:
        path (str): Path to find (from `struct_repo`).
        path_patches (List[str]): List of paths to check (from git patches, = modified files only).

    Returns:
        Tuple[str, None]: Full path (from git patches) if match. Else None.
    """
    
    finder = [pth for pth in path_patches if Path(path).name == Path(pth).name and path in pth]
    return finder[0] if finder else None

def get_struct_repo_patches(repo_tree: Path, patches: dict) -> dict:  # pragma: no cover
    """Builds and returns struct repo containing info from git patches.

    Args:
        repo_tree (Path): Path to `struct_repo.json`.
        patches (dict): Patches data.

    Returns:
        dict: Nested struct repo data adapted to git patches visualization.
        patches_tree = {
            "name": "hello",
            "path": "package:hello",
            "NLOC": 10,               # mandatory to compute circles's size
            "status": "changed",      # changed / unchanged
            "modifications": 20,      # insertions + deletions
            "children": [...],
        }
    """
    with open(repo_tree, "r") as fin:
        repo_data = json.load(fin)

    patches_tree = _build_struct_repo_patches(repo_data, patches)

    return patches_tree
