import tkinter as tk
from nobvisual.tkinter_circlify import tkcirclify
from nobvisual.circlifast import circlifast
from nobvisual.colorize import color_by_name_pattern, color_by_value
from nobvisual.helpers import from_circlify_to_nobvisual
from loguru import logger
from tucan.struct_common import (
    FIELDS_INTENSIVE,
    FIELDS_EXTENSIVE,
    FIELDS_SIZES,
    FIELDS_EXT_DICT,
    FIELDS_INT_DICT,
    FIELDS_SIZES_DICT,
)


ANALYSIS_FIELDS = " ; ".join(
    [
        f"{key}:{value}"
        for key, value in (
            FIELDS_EXT_DICT | FIELDS_INT_DICT | FIELDS_SIZES_DICT
        ).items()
    ]
)


def show_tree_nob(
    repo_data: dict, package: str, colorby: str, patterns_dict: dict = None
):
    """repo_data is the nested dict given by tucan struct-repo command.
    
        { 
            name: root
            CCN : 12
            LPS : 4
            children : [
                ___sub items___
            ]
        }
    
    
    """
    nobj = [_rec_simplfy_repo(repo_data,colorby)]

    title = f"{package} colored by "
    invert = False

    if colorby in ["PTN"]:
        title += "patterns in names"
        legend = [(f"*{key}*", value) for key, value in patterns_dict.items()]
        color_by_name_pattern(nobj, legend)
    elif colorby in FIELDS_INTENSIVE + FIELDS_EXTENSIVE + FIELDS_SIZES:
        invert = False
        title += (FIELDS_EXT_DICT | FIELDS_INT_DICT | FIELDS_SIZES_DICT).get(
            colorby, "Error"
        )
        title += f" ({colorby})"
        maxval= None
        cmap = "BuRd"
        if colorby in ["HDF", "LPS", "CST", "LPS", "CCN"]:
            cmap = "rainbow_WhRd"
        elif colorby in [
            "NLOC",
            "ssize",
        ]:
            cmap = "YlOrBr"
        elif colorby in ["HTM"]:
            cmap = "rainbow_WhBr"
        if colorby in ["MI"]:
            cmap = "BuRd"
            invert = True
        
        # if colorby == "HDF":
        #    maxval=200.
        # elif colorby == "CST":
        #    maxval=4000.
        legend = color_by_value(
            nobj, "colorvar", invert=invert, tolcmap=cmap, logarithmic=False, max_val=maxval
        )

    else:
        logger.warning(f"color by {colorby} is not an option")

    circles = circlifast(nobj, show_enclosure=False)
    draw_canvas = tkcirclify(
        from_circlify_to_nobvisual(circles), legend=legend, title=title
    )
    draw_canvas.show_names(level=2)
    tk.mainloop()


def _rec_simplfy_repo(nobj: dict, colorby: str, path:list=None) -> dict:
#def _rec_simplfy_repo(nobj: dict, colorby: str) -> dict:
    """
    Simplification of the repository data.
    We keep a COLOR based upon COLORBY parameter
    The value of  COLORBY in Colorvar 
    A text describing the item  
    
    """
    text = "\n".join(
        [f"{key}: {value}" for key, value in nobj.items() if key not in ["children"]]
    )

    colorvar = nobj.get(colorby, None)
    if colorby in FIELDS_EXTENSIVE + FIELDS_SIZES:
        if nobj.get("children", []) != []:
            colorvar = 0

    if path is None:
        path=[]
    out = {
        "name": nobj["name"],
        "id": path,
        "datum": nobj.get("NLOC", None),
        "text": text,
        "color": None,
        "path": path,
        "colorvar": colorvar,
        "children": [],
    }
    for child in nobj.get("children", []):
        #out["children"].append(_rec_simplfy_repo(child,colorby))
        out["children"].append(_rec_simplfy_repo(child,colorby, path+[child["name"]]))
    return out




# def merge_file_and_repo_data(file_data, repo_data,colorby):
#     """Augment the simplified repo data by the procedures data"""
    
#     # First the simpified data...
#     simple_repo = [_rec_simplfy_repo(repo_data,colorby)]



#     def _ref_incontain(file_data, list_item)->list:
#         """Retur the data from the files"""
#         out = {}
#         for item in set(list_item):
#             logger.success(">>>>>>"+item)
#             sub_data = file_data[item]
#             if sub_data["contains"]:
#                out.update( _ref_incontain(file_data, sub_data["contains"]))

#     def _rec_aggreg_files(item)-> dict:
#         """Re-Agregate the repo , and search for the files"""   
#         out = {
#             key:value for key, value in item.items() if key not in ["children"]
#         }

#         if item["children"] == []:          # case of files
#             tgt = "/".join(item["path"])

#             fdata = file_data.get(tgt,None)

#             if fdata is None:
#                 logger.warning(f"Could not find {tgt}")

#             cont = list(fdata.values())[0]["contains"]
#             out["children"] = _ref_incontain(fdata, cont)        
#             logger.success(cont)
#         else: 
#             out["children"] =[]
#             for child in item["children"]:
#                 out["children"].append(_rec_aggreg_files(child))
    

#     out = _rec_aggreg_files(simple_repo[0])

#     return out
    

