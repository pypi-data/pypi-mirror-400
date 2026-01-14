from pathlib import Path

def create_scriptjs(param: dict) -> str:
    """Auto generate a script.js for tree show js.
    script.js is used to load struct data and call nobvisualjs.

    Args:
        param (dict): Param from mmap_in.yml

    Returns:
        str: Plain text of script.js
    """

    git_directory = Path(param["path"]).parent
    package_name = param["package"]

    code = f"""
import {{dynamicNobvisualjs}} from '/nobvisualjs/main.js'
import {{addSubtitle}} from '/nobvisualjs/settings.js'

/**
 * Load struct data and call nobvisual js.
 * @param {{string}} data_path Path to the struct_repo.json (handle by server)
 * @param {{string}} repo_name Name of the repo (param from mmap_in.yml)
 * @param {{string}} repo_path Path to the repo (param from mmap_in.yml)
 */
async function tree_showjs(data_path, repo_name, repo_path) {{
    const data = await d3.json(data_path)
    dynamicNobvisualjs(data, repo_name, repo_path)
    addSubtitle(`Navigate through the repo with your cursor.<br>
    Click + CTRL or CMD to open the code.`)
}}

tree_showjs('/struct_repo.json', '{package_name}', '{git_directory}')
"""

    return code