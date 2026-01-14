#!/usr/bin/env python
"""
cli.py

Command line interface for tools in MaraudersMaps
"""
import click
import os
import importlib.resources
from loguru import logger
from tucan.struct_common import FIELDS_INTENSIVE, FIELDS_EXTENSIVE, FIELDS_SIZES, FIELDS_EXT_DICT,FIELDS_INT_DICT,FIELDS_SIZES_DICT

ANALYSIS_FIELDS =" ; ".join( [f"{key}:{value}" for key, value in (FIELDS_EXT_DICT | FIELDS_INT_DICT | FIELDS_SIZES_DICT).items()])


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def add_version(f):
    """
    Add the version of the tool to the help heading.
    :param f: function to decorate
    :return: decorated function
    """
    import maraudersmap

    doc = f.__doc__
    f.__doc__ = (
        "Package "
        + maraudersmap.__name__
        + " v"
        + maraudersmap.__version__
        + "\n\n"
        + doc
    )

    return f


@click.group()
@add_version
def main_cli():
    """
    \b
            ---------------    Marauders map  --------------------
            You are now using the Command line interface of Marauders map package,
            a set of tools created at CERFACS (https://cerfacs.fr).
            It creates callgraphs for python and fortran projects.
    \b
            For the impatients;
            Use `mmap cg_fast`for a quick generation on a single file
    \b
            For larger projects:
            1 - Use `mmap anew` to create your main control file `mmap_in.yml`,
            2 - Edit `mmap_in.yml` to describe your project
            3 - Use `cg-gen` to pre-compute the callgraph (can take minutes)
            4 - Use `cg-show` with the different options to explore the callgraph
    """
    pass


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
def anew(file):
    """Create the default control file mmap_in.yml"""
    from pkg_resources import resource_filename
    import os, shutil

    write = True
    if os.path.isfile(file):
        msg = f"File {file} already exists. Overwrite ? [y/N] "
        if input(msg).lower() == "n":
            write = False
    if write:
        logger.info(f"Generating template inputfile {file} for maraudersmap.")
        shutil.copy2(
            resource_filename(__name__, "./mmap_in.yml"),
            file,
        )
    logger.success(f"File {file} created. Edit this file to set up your project...")


main_cli.add_command(anew)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="MMAP Control file (.yml)",
)
@click.option(
    "-p",
    "--include_procedures",
    is_flag=True,
    help="Include procedures in struct_repo.json (heavier)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def tree_gen(file, verbose,include_procedures):
    """Create the tree of functions from sourcecode.

    Output is (name-of-pkg)/func_tree.json

    Need the MMAP Control file to find the sources,
    and obviously the sources themselves...
    """
    from loguru import logger
    from tucan.package_analysis import (
        run_struct_all_repo,
    )
    from tucan.cli_pprinter import struct_summary_repo

    from json import dump as jdump
    from maraudersmap.mmap_startlog import mmap_startlog

    mmap_startlog(verbose)
    param = prepare_cmd(file)

    struct_repo,struct_files = run_struct_all_repo(
        param["path"],
        forbidden_patterns=param["forbidden_patterns"],
        mandatory_patterns=param["mandatory_patterns"],
        verbose=verbose,
        include_procedures=include_procedures)

    print(struct_summary_repo(struct_repo))

    outdir = ensure_dir(param["package"])
    newfile = (outdir / "struct_repo.json")
    with open(newfile, "w") as fout:
        jdump(struct_repo, fout, indent=2, sort_keys=True)
    logger.success(f"Repo Data dumped to {newfile}")
    newfile = (outdir / "struct_files.json")
    with open(newfile, "w") as fout:
        jdump(struct_files, fout, indent=2, sort_keys=True)
    logger.success(f"File Data dumped to {newfile}")

main_cli.add_command(tree_gen)


@click.command(help=f"""
    Visualize MMAP trees
           
    Possible values are {ANALYSIS_FIELDS}""")
@click.argument(
    "colorby",
    nargs=1,
    type=click.Choice(FIELDS_INTENSIVE + FIELDS_EXTENSIVE + FIELDS_SIZES + ["PTN"]),
)
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="MMAP Control file (.yml)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def tree_show(colorby, file, verbose):
    f"""Visualize MMAP trees
    """
    import json
    from pathlib import Path

    from maraudersmap.mmap_startlog import mmap_startlog
    from maraudersmap.show_tree_nob import show_tree_nob

    mmap_startlog(verbose)

    param = prepare_cmd(file)

    # Select source
    repo_tree = Path(param["package"]) / "struct_repo.json"
    if not repo_tree.exists():
        msg = f"Tree info  {str(repo_tree)} is missing. Use `mmap tree-gen` to create it."
        logger.warning(msg)
        raise FileNotFoundError(msg)

    with open(repo_tree, "r") as fin:
        repo_data = json.load(fin)
    
    show_tree_nob(repo_data,param["package"], colorby,patterns_dict=param["color_rules"])

main_cli.add_command(tree_show)


@click.command(
    help=f"""
    Visualize MMAP trees with d3JS"""
)
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="MMAP Control file (.yml)",
)
@click.option(
    "--port",
    "-p",
    type=str,
    default=None,
    help="Port",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def tree_showjs(file, port, verbose):
    f"""Visualize MMAP trees
    """
    from maraudersmap.mmap_startlog import mmap_startlog
    from pathlib import Path
    from moonframe.app_builder import build_app_treeshow
    from moonframe.application import serve_app
    from maraudersmap.full_graph_actions import build_hex_color_rules

    mmap_startlog(verbose)

    param = prepare_cmd(file)
    repo_name = Path(param["package"]) 
    # source
    repo_tree = repo_name / "struct_repo.json"
    if not repo_tree.exists():
        msg = (
            f"Tree info  {str(repo_tree)} is missing. Use `mmap tree-gen` to create it."
        )
        logger.warning(msg)
        raise FileNotFoundError(msg)

    color_rules = build_hex_color_rules(param["color_rules"])

    # create script js
    app = build_app_treeshow(
        filepath=repo_tree,
        repo_path=Path(param["path"]),
        repo_name=repo_name,
        color_rules=color_rules,
    )

    # server
    serve_app(app, port)


main_cli.add_command(tree_showjs)


# @click.command()
# @click.option(
#     "--file",
#     "-f",
#     type=str,
#     default="./mmap_in.yml",
#     help="Input file with a custom name (.yml)",
# )
# @click.option(
#     "-v",
#     "--verbose",
#     is_flag=True,
#     show_default=True,
#     default=False,
#     help="Verbose mode",
# )
# def treefile(file, verbose):
#     """Create the tree of files from sourcecode.

#     Output is (name-of-pkg)/file_tree.json

#     Need the MMAP Control file to find the sources,
#     and obviously the sources themselves...
#     """
#     from maraudersmap.macro_tree import get_macro_tree
#     from networkx import node_link_data
#     from json import dump as jdump
#     from maraudersmap.mmap_startlog import mmap_startlog

#     mmap_startlog(verbose)
#     param = prepare_cmd(file)
#     macro_graph = get_macro_tree(
#         param["path"],
#         param["package"],
#     )
#     outdir = ensure_dir(param["package"])
#     with open(outdir / "file_tree.json", "w") as fout:
#         jdump(node_link_data(macro_graph), fout, indent=4, sort_keys=True)
#     logger.success(f"Generating {param['package']} / file_tree.json.")


# main_cli.add_command(treefile)


# @click.command()
# @click.argument(
#     "rules",
#     nargs=1,
#     type=click.Choice(["python", "fortran"]),
# )
# @click.option(
#     "-v",
#     "--verbose",
#     is_flag=True,
#     show_default=True,
#     default=False,
#     help="Verbose mode",
# )
# def regexp_input(rules, verbose):
#     """Create a score rules file"""
#     from pkg_resources import resource_filename
#     import os, shutil
#     from maraudersmap.mmap_startlog import mmap_startlog

#     mmap_startlog(verbose)
#     write = True
#     if rules == "python":
#         file = "./python_rc_default.yml"
#         if os.path.isfile(file):
#             msg = f"File {file} already exists. Overwrite ? [y/N] "
#             if input(msg).lower() == "n":
#                 write = False
#     elif rules == "fortran":
#         file = "./fortran_rc_default.yml"
#         if os.path.isfile(file):
#             msg = f"File {file} already exists. Overwrite ? [y/N] "
#             if input(msg).lower() == "n":
#                 write = False
#     if write:
#         logger.info(f"Generating dummy regexp inputfile {file} for maraudersmap score.")
#         shutil.copy2(
#             resource_filename(__name__, f"{file}"),
#             file,
#         )
#     logger.info(f"File {file} created. Edit this file to customize your own rules.")


# main_cli.add_command(regexp_input)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="MMAP Control file (.yml)",
)
@click.argument(
    "rules",
    type=str,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def score(rules, file, verbose):
    """
    Add score to the MMAP tree of functions

    Need the MMAP Control file to find the sources,

    RULES is the regexp&structure set of rules.
    These rules can be generated through mmap regexp-input (can be edited)
    """
    import json, os
    from networkx import node_link_data, node_link_graph
    from json import dump as jdump
    from maraudersmap.score import get_score
    from pathlib import Path
    from maraudersmap.mmap_startlog import mmap_startlog

    mmap_startlog(verbose)

    param = prepare_cmd(file)

    func_tree = Path(param["package"]) / "func_tree.json"
    if not func_tree.exists():
        logger.warning(
            f"Function tree {str(func_tree)} is missing. Use `mmap tree` to create it."
        )

    with open(func_tree, "r") as fin:
        nld = json.load(fin)
    tree_graph = node_link_graph(nld)
    score_graph = get_score(param["path"], tree_graph, rules)
    with open(Path(param["package"]) / "func_tree_score.json", "w") as fout:
        jdump(node_link_data(score_graph), fout, indent=4, sort_keys=True)
    logger.success(f"Generating {param['package']}/func_tree_score.json with scores.")


main_cli.add_command(score)


@click.command()
@click.argument(
    "pattern",
    type=str,
)
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="MMAP Control file (.yml)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def grep(file, pattern, verbose):
    """
    Visualize where a specific pattern appears in the codebase.
    """
    import json
    from pathlib import Path
    import tkinter as tk
    from nobvisual.tkinter_circlify import tkcirclify
    from nobvisual.circlifast import circlifast
    from nobvisual.colorize import color_by_value
    from nobvisual.helpers import from_circlify_to_nobvisual
    from maraudersmap.grep import set_grep_codebase
    from maraudersmap.mmap_startlog import mmap_startlog
    from maraudersmap.show_tree_nob import _rec_simplfy_repo

    mmap_startlog(verbose)
    param = prepare_cmd(file)
    path_struct = Path(param["package"]) / "struct_repo.json"
    path_file = Path(param["package"]) / "struct_files.json"
    path_repo = param["path"]
    if not path_struct.exists() or not path_file.exists():
        logger.warning(
            f"{str(path_file)} and/or {str(path_struct)} is missing. Use `mmap tree-gen` to create it."
        )
    with open(path_struct, "r") as f:
        struct_r = json.load(f)
    with open(path_file, "r") as f:
        struct_f = json.load(f)

    set_grep_codebase(pattern, struct_r, path_repo, struct_f)
    nobj = [_rec_simplfy_repo(struct_r, "grep")]
    legend = color_by_value(nobj, "colorvar", tolcmap="rainbow_WhRd")
    circles = circlifast(nobj, show_enclosure=False)
    draw_canvas = tkcirclify(from_circlify_to_nobvisual(circles), legend=legend)
    draw_canvas.show_names(level=2)
    tk.mainloop()


main_cli.add_command(grep)


# @click.command()
# @click.argument("macro_graph", type=str)
# @click.option(
#     "--file",
#     "-f",
#     type=str,
#     default="./coverage.json",
#     help="Coverage json file from gcov",
# )
# def coverage_tree(macro_graph, file):
#     """Dump .json of mmap coverage macro tree graph."""
#     import json
#     from networkx import node_link_data, node_link_graph
#     from json import dump as jdump
#     from maraudersmap.coverage import get_coverage_tree

#     with open(macro_graph, "r") as fin:
#         nld = json.load(fin)
#     macro_graph = node_link_graph(nld)

#     coverage_graph = get_coverage_tree(macro_graph, file)

#     with open(f"coverage_tree.json", "w") as fout:
#         jdump(node_link_data(coverage_graph), fout, indent=4, sort_keys=True)

#     logger.success(f"Generating coverage_tree.json, use show command to see your results.")


# main_cli.add_command(coverage_tree)


@click.command()
@click.argument(
    "vgfile",
    nargs=1,
    type=str,
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-x",
    "--includeexternal",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include data beyond source objects (i.e. compiler artefacts)",
)
@click.option(
    "-n",
    "--includenegligible",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include data of negligible objects (0.00% of time)",
)
def vg_gen(vgfile, verbose, includeexternal, includenegligible):
    """Generate a Network-X directed graph from a Valgrind output.

    The file expected is generated by Valgrind v3.18.1 (With 3.15 it failed) :
    
    \b
    callgrind_annotate --tree=both --auto=yes  --inclusive=yes --context=2  ./callgrind.out.2489
    
    \b
    - tree both to get also the edges
    - with context (to get where were the sources)
    - reduce context for a lighter version
    - inclusive to aggregate all times for each level
    """
    from networkx import node_link_data
    from json import dump as jdump
    from maraudersmap.valgrindload import parse_valgrind_data,get_potential_nodes
    from maraudersmap.mmap_startlog import mmap_startlog

    mmap_startlog(verbose)
    with open(vgfile, "r") as fin:
        data = fin.readlines()

    only_sources = not includeexternal
    skip_negligible = not includenegligible
    vg_graph = parse_valgrind_data(data, only_sources, skip_negligible)

   

    with open("valgrindgraph.json", "w") as fout:
        jdump(node_link_data(vg_graph), fout, indent=4, sort_keys=True)
    with open("valgrindnodes.json", "w") as fout:
        jdump(get_potential_nodes(vg_graph), fout, indent=4, sort_keys=True)
    
    logger.success(f"Generating valgrindgraph.json, valgrindnodes.json.")


main_cli.add_command(vg_gen)


@click.command()
@click.argument(
    "vgfile",
    nargs=1,
    type=str,
)
@click.option(
    "-x",
    "--includeexternal",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include data beyond source objects (i.e. compiler artefacts)",

)
@click.option(
    "-n",
    "--includenegligible",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include data of negligible objects (0.00% of time)",
)
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["pydot", "pyvis"]),
    default="pyvis",
    help="Backend for rendering",
)
@click.option(
    "--color",
    "-c",
    type=click.Choice(
        [
            "lvl",
            "ptn",
        ]
    ),
    default="lvl",
    help="""Coloring strategy

\b  
    lvl  : by API lvl (0 - low level, 1- high level)
    ptn  : by the patterns in the mmap_in.yml  (must be provided!)

    
""",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--load",
    is_flag=True,
    show_default=True,
    default=False,
    help="Load result in default webbrowser",
)
def vg_show(
    vgfile, file, backend, color, verbose, load, includeexternal, includenegligible
):
    """Visualize Valgrind on a project defined in mmap_in.yml"""
    from maraudersmap.full_graph_actions import show_graph, complete_valgrind_data
    from maraudersmap.mmap_startlog import mmap_startlog
    from networkx import node_link_data
    from json import dump as jdump
    from pathlib import Path
    from maraudersmap.valgrindload import parse_valgrind_data

    mmap_startlog(verbose)
    with open(vgfile, "r") as fin:
        data = fin.readlines()
    only_sources = not includeexternal
    skip_negligible = not includenegligible
    vg_graph = parse_valgrind_data(data, only_sources, skip_negligible)

    outdir = Path(".")

    if os.path.isfile(file):
        param = prepare_cmd(file)
        outdir = ensure_dir(param["package"])

    else:
        param = {"color_rules": {}, "clean_graph": {}}

    with open(outdir / "valgrindgraph.json", "w") as fout:
        jdump(node_link_data(vg_graph), fout, indent=4, sort_keys=True)
    logger.success(f"Generating {outdir}/valgrindgraph.json.")

    vg_graph = complete_valgrind_data(vg_graph)
    # visualise
    show_graph(
        vg_graph,
        backend=backend,
        color=color,
        patterns=param["color_rules"],
        remove_patterns=param["clean_graph"].get("remove_patterns", None),
        hyperconnect=param["clean_graph"].get("remove_hyperconnect", None),
        subgraph_roots=param["clean_graph"].get("subgraph_roots", None),
        load=load,
        prefix="valgrind",
    )


main_cli.add_command(vg_show)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def im_gen(file, verbose):
    """Generate the imports graph"""
    import os
    from maraudersmap.imports import get_importsgraph
    from networkx import node_link_data
    from json import dump as jdump
    from maraudersmap.mmap_startlog import mmap_startlog

    mmap_startlog(verbose)
    param = prepare_cmd(file)
    wkdir = os.getcwd()
    imports_graph = get_importsgraph(
        os.path.join(wkdir, param["path"]),
        forbidden_patterns=param["forbidden_patterns"],
        mandatory_patterns=param["mandatory_patterns"]
    )
    outdir = ensure_dir(param["package"])
    with open(outdir / "importsgraph.json", "w") as fout:
        jdump(node_link_data(imports_graph), fout, indent=4, sort_keys=True)
    logger.success(f"Generating {param['package']}/importsgraph.json.")


main_cli.add_command(im_gen)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["pydot", "pyplot", "plotly", "pyvis", "mvp"]),
    default="pyvis",
    help="Backend for rendering",
)
@click.option(
    "--color",
    "-c",
    type=click.Choice(
        [
            "type",
            #            "lang",
            #            "cplx",
            "rlvl",
            "lvl",
            "ptn",
        ]
    ),
    default="ptn",
    help="""Coloring strategy

\b  
    type : by type (subroutine, method, object)
    lvl  : by API lvl (0 - low level, 1- high level)
    ptn  : by the patterns in the mmap_in.yml 

    
""",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--load",
    is_flag=True,
    show_default=True,
    default=False,
    help="Load result in default webbrowser",
)
def im_show(file, backend, color, verbose, load):
    """Visualize importgraph on a project defined in mmap_in.yml"""
    import json
    from pathlib import Path
    import networkx as nx
    from maraudersmap.full_graph_actions import show_graph, complete_importgraph_data
    from maraudersmap.mmap_startlog import mmap_startlog

    mmap_startlog(verbose)
    # load files
    param = prepare_cmd(file)
    graph_json = Path(param["package"]) / "importsgraph.json"
    with open(graph_json, "r") as fin:
        nld = json.load(fin)
    cgs_nx = nx.node_link_graph(nld)

    cgs_nx = complete_importgraph_data(cgs_nx)
    # visualise
    show_graph(
        cgs_nx,
        backend=backend,
        color=color,
        patterns=param["color_rules"],
        remove_patterns=param["clean_graph"].get("remove_patterns", None),
        hyperconnect=None,
        subgraph_roots=param["clean_graph"].get("subgraph_roots", None),
        load=load,
        prefix="imports",
    )


main_cli.add_command(im_show)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)

@click.option(
    "-t",
    "--use_valgrind_trace",
    type=str,
    default=None,
    help="Use valgrind trace for calls detection",
)

def cg_gen(file, verbose,use_valgrind_trace):
    """Gen callgraph ddb of a project defined mmap_in.yml"""
    import json
    from maraudersmap.callgraph import get_callgraph
    from maraudersmap.valgrindload import parse_valgrind_data
    from networkx import node_link_data
    from maraudersmap.mmap_startlog import mmap_startlog

    mmap_startlog(verbose)
    param = prepare_cmd(file)

    vg_graph=None
    if use_valgrind_trace is not None :
        with open(use_valgrind_trace, "r") as fin:
            data = fin.readlines()
        vg_graph = parse_valgrind_data(data, True, False)

    cpp_directives = param.get("cpp_directives", None)
    if cpp_directives is None:
        cpp_definitions = []
    else:
        cpp_definitions=[]
        for key,value in cpp_directives.items():
            if value is not False:
                cpp_definitions.append(key)

    callgraph, _ = get_callgraph(
        param["path"],
        param["context"],
        forbidden_patterns=param["forbidden_patterns"],
        mandatory_patterns=param["mandatory_patterns"],
        cpp_directives=cpp_definitions,
        valgrind_graph=vg_graph

        
    )
    outdir = ensure_dir(param["package"])
    with open(outdir / "callgraph.json", "w") as fout:
        json.dump(node_link_data(callgraph), fout, indent=4, sort_keys=True)
    logger.success(f"Generating {param['package']}/callgraph.json.")


main_cli.add_command(cg_gen)


@click.command()
@click.argument(
    "file",
    nargs=1,
    type=str,
)
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["pydot", "pyplot", "plotly", "pyvis", "mvp"]),
    default="pyvis",
    help="Backend for rendering",
)
@click.option(
    "--merge",
    "-m",
    is_flag=True,
    show_default=True,
    default=False,
    help="""Merge childs of containers (reduce graph)

\b  
    Each container will merge its childs eg:
    - methods  merged in their object
    - subroutines  merged in their module

    This makes graphs easier to read and faster to render.
        
""",
)
@click.option(
    "--color",
    "-c",
    type=click.Choice(
        [
            "type",
            "lang",
            "cplx",
            "lvl",
            "rlvl",
        ]
    ),
    default="type",
    help="""Coloring strategy

\b  
    type : by type (subroutine, method, object)
    lang : by language (fortran, cpp, c, python)
    cplx : by complexity 
    lvl  : by API lvl (0 - low level, 1- high level)
    ptn  : by the patterns in the mmap_in.yml 

    
""",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--load",
    is_flag=True,
    show_default=True,
    default=False,
    help="Load result in default webbrowser",
)
def cg_fast(file, backend, merge, color, verbose, load):
    """
    Fast Gen.& Visualize callgraph on single file (no mmap_in.yml)
    """
    from maraudersmap.callgraph import get_callgraph
    from maraudersmap.mmap_startlog import mmap_startlog
    from maraudersmap.full_graph_actions import show_graph, complete_callgraph_data

    mmap_startlog(verbose)

    cgs_nx. _ = get_callgraph(
        file,
        file,
    )

    cgs_nx = complete_callgraph_data(cgs_nx, merge_containers=merge, nocalls=False)
    show_graph(
        cgs_nx,
        backend=backend,
        color=color,
        patterns=None,
        remove_patterns=None,
        hyperconnect=10,
        subgraph_roots=None,
        load=load,
        prefix="calls",
    )


main_cli.add_command(cg_fast)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["pydot", "pyplot", "plotly", "pyvis", "mvp"]),
    default="pyvis",
    help="Backend for rendering",
)
@click.option(
    "--nocalls",
    "-n",
    is_flag=True,
    show_default=True,
    default=False,
    help="Remove Calls from callgraph (structure only)",
)
@click.option(
    "--merge",
    "-m",
    is_flag=True,
    show_default=True,
    default=False,
    help="""Merge childs of containers (reduce graph)

\b  
    Each container will merge its childs eg:
    - methods  merged in their object
    - subroutines  merged in their module

    This makes graphs easier to read and faster to render.
        
""",
)
@click.option(
    "--color",
    "-c",
    type=click.Choice(
        [
            "type",
            "lang",
            "cplx",
            "lvl",
            "rlvl",
            "ptn",
            "grep",
            "conta",
        ]
    ),
    default="type",
    help="""Coloring strategy

\b  
    type : by type (subroutine, method, object)
    lang : by language (fortran, cpp, c, python)
    cplx : by complexity 
    lvl  : by API lvl (0 - low level, 1- high level)
    ptn  : by the patterns in the mmap_in.yml 
    grep : by grep patterns  in the mmap_in.yml
    
    
""",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
@click.option(
    "-l",
    "--load",
    is_flag=True,
    show_default=True,
    default=False,
    help="Load result in default webbrowser",
)
def cg_show(file, backend, merge, color, nocalls, verbose, load):
    """Visualize callgraph on a project defined in mmap_in.yml"""
    import json
    from pathlib import Path
    import networkx as nx
    from maraudersmap.full_graph_actions import show_graph, complete_callgraph_data
    from maraudersmap.mmap_startlog import mmap_startlog

    mmap_startlog(verbose)
    # load files
    param = prepare_cmd(file)
    graph_json = Path(param["package"]) / "callgraph.json"
    with open(graph_json, "r") as fin:
        nld = json.load(fin)
    cgs_nx = nx.node_link_graph(nld)
    # visualise
        

    cgs_nx = complete_callgraph_data(cgs_nx, merge_containers=merge, nocalls=nocalls)

    try: 
        show_graph(
            cgs_nx,
            backend=backend,
            color=color,
            patterns=param["color_rules"],
            remove_patterns=param["clean_graph"].get("remove_patterns", None),
            hyperconnect=param["clean_graph"].get("remove_hyperconnect", None),
            subgraph_roots=param["clean_graph"].get("subgraph_roots", None),
            grep_patterns=param.get("grep_patterns", None),
            load=load,
            rootpath=param["path"],
            prefix="calls",
        )
    except RuntimeError as e:
        print(e.__cause__)


main_cli.add_command(cg_show)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
@click.option(
    "--port",
    "-p",
    type=str,
    default=None,
    help="Port",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def cg_showjs(file, port, verbose):
    """Visualize callgraph with d3js"""
    from maraudersmap.mmap_startlog import mmap_startlog
    from pathlib import Path
    from moonframe.app_builder import build_app_network
    from moonframe.application import serve_app
    from maraudersmap.full_graph_actions import build_hex_color_rules

    mmap_startlog(verbose)

    param = prepare_cmd(file)
    # source
    repo_name = Path(param["package"])
    repo_callgraph = repo_name / "callgraph.json"
    if not repo_callgraph.exists():
        msg = f"Callgraph info  {str(repo_callgraph)} is missing. Use `mmap cg-gen` to create it."
        logger.warning(msg)
        raise FileNotFoundError(msg)

    color_rules = build_hex_color_rules(param["color_rules"])

    # create script js
    app = build_app_network(
        filepath=repo_callgraph,
        repo_path=Path(param["path"]),
        repo_name=repo_name,
        color_rules=color_rules,
    )

    # server
    serve_app(app, port)


main_cli.add_command(cg_showjs)


@click.command()
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="Input file with a custom name (.yml)",
)
@click.option(
    "--removefolder",
    "-r",
    is_flag=True,
    default=False,
    help="Remove folders from analysis",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def scatter(file, removefolder, verbose):
    """Visualize code metrics with an interactive scatter plot"""
    from maraudersmap.mmap_startlog import mmap_startlog
    from maraudersmap.scatter import (
        structjson2csv,
        standardize_keys,
        filter_list_dict,
    )
    from pathlib import Path
    import json
    from csv import DictWriter
    from moonframe.app_builder import build_app_scatter
    from moonframe.application import serve_app

    mmap_startlog(verbose)

    # source
    param = prepare_cmd(file)
    repo_csv = Path(param["package"]) / "struct_repo_flat.csv"
    write = True
    if repo_csv.exists():
        msg = f"File {repo_csv} already exists. Overwrite ? [y/n] "
        if input(msg).lower() == "n":
            write = False
    # create input CSV
    if write:
        repo_tree = Path(param["package"]) / "struct_repo.json"
        if not repo_tree.exists():
            msg = f"Tree info  {str(repo_tree)} is missing. Use `mmap tree-gen` to create it."
            logger.warning(msg)
            raise FileNotFoundError(msg)

        with open(repo_tree, "r") as fin:
            repo_data = json.load(fin)

        flat_struct = structjson2csv(repo_data)
        if removefolder:
            flat_struct = filter_list_dict(flat_struct, "type", "folder")
        csv_data = standardize_keys(flat_struct)

        with open(
            repo_csv,
            "w",
        ) as file:
            writer = DictWriter(file, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
        logger.success(f"`struct_repo_flat.csv` was sucessfully created.")

    app = build_app_scatter(repo_csv, ",")
    serve_app(app)


main_cli.add_command(scatter)


@click.command(
    help=f"""View git patches in a tree graph.
    
    Takes as argument the path to the folder where all patches (.patches) are stored. 
    
    This graph opens automatically in your default browser (hosted locally). """
)
@click.argument(
    "path",
    type=str,
)
@click.option(
    "--file",
    "-f",
    type=str,
    default="./mmap_in.yml",
    help="MMAP Control file (.yml)",
)
@click.option(
    "--port",
    "-p",
    type=str,
    default=None,
    help="Port",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Verbose mode",
)
def git_patches(path, file, port, verbose):
    from maraudersmap.mmap_startlog import mmap_startlog
    from pathlib import Path
    import json
    from moonframe.app_builder import build_app_treeshow
    from moonframe.application import serve_app
    from maraudersmap.git_patches import (
        find_patches,
        get_struct_repo_patches,
    )

    mmap_startlog(verbose)

    write = True
    param = prepare_cmd(file)
    repo_name = Path(param["package"])
    # source
    repo_tree = repo_name / "struct_repo.json"
    if not repo_tree.exists():
        msg = (
            f"Tree info  {str(repo_tree)} is missing. Use `mmap tree-gen` to create it."
        )
        raise FileNotFoundError(msg)
    # assert patches_folder exists
    patches_folder = Path(path)
    if not patches_folder.exists():
        msg = (
            f"Can't find patch directory '{str(patches_folder)}'."
        )
        raise FileNotFoundError(msg)
    patchfile = repo_name / "git_patches.json"

    if patchfile.exists():
        msg = f"File {patchfile} already exists. Overwrite ? [y/N] "
        if input(msg).lower() == "n":
            write = False
    
    if write: # write data
        patches = find_patches(path, verbose)
        patches_tree = get_struct_repo_patches(repo_tree, patches)

        with open(patchfile, "w") as fout:
            json.dump(patches_tree, fout, indent=2)
        logger.success(f"File Data dumped to {patchfile}")


    # call moonframe
    app = build_app_treeshow(
        filepath=patchfile,
        repo_path=Path(param["path"]),
        repo_name=repo_name,
        color_rules={},
    )
    # server
    serve_app(app, port)


main_cli.add_command(git_patches)


########################################################
####################### UTILITIES ######################
########################################################


def dump_json(nx_data, type_)-> dict:
    import json
    from networkx import node_link_data

    fname = f"mmap_{type_}_graph.json"
    with open(fname, "w") as fout:
        json.dump(node_link_data(nx_data), fout, indent=4, sort_keys=True)
    logger.info(f"Graph dumped as {fname}")


def prepare_cmd(file) -> dict:
    """Read and check the control file of MMAP.
    
    The missing keys will be taken from the default input file
    """
    from yaml import safe_load
    from pathlib import Path

    with importlib.resources.open_text("maraudersmap", "mmap_in.yml") as default_file:
        out_params =  safe_load(default_file)

    ctrl_file = Path(file)
    if not ctrl_file.exists():
        logger.warning(
            f"File {file} does not exist. Use  >mmap anew  to create a new one"
        )
        exit()

    with open(file, "r") as fin:
        param = safe_load(fin)

    if param is None:
        raise RuntimeError(f"No parameters found in {file}")

    # update path and context, mandatory
    tgt = Path(param["path"])
    if not tgt.exists():
        raise RuntimeError(f"Path {param['path']} not found")
    if "context" not in param:
        param["context"] = param["path"]


    out_params.update(param)
    return out_params


def ensure_dir(dir):
    """As name says

    So short we could remove it."""
    from pathlib import Path

    outdir = Path.cwd().absolute() / dir
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir
