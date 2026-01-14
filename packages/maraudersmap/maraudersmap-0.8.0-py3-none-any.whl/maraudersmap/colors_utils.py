
from tol_colors import tol_cmap
from math import log10
from matplotlib import colors as mplcolors
import matplotlib.colors as mc
import colorsys
import numpy as np
from loguru import logger

def shade_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    if amount>0:
        l= 1 - amount * (1 - c[1])
    else:
        l= (1+amount) *  c[1]

    return colorsys.hls_to_rgb(c[0], l, c[2])


def brighten_color(color, brighter: float = 0.7) -> str:
    """

    To brighten the color, use a float valuecloser to 1

    """
    tuple_rgb = mplcolors.to_rgba(color)

    if brighter < 0:
        return tuple_rgb

    out = (
        (tuple_rgb[0] * (1 - brighter) + brighter),
        (tuple_rgb[1] * (1 - brighter) + brighter),
        (tuple_rgb[2] * (1 - brighter) + brighter),
        tuple_rgb[3],
    )
    return mplcolors.to_hex(out)


def darken_color(color, darker: float = 0.4) -> str:
    """

    To darken the color, use a float valuecloser to 1

    """
    tuple_rgb = mplcolors.to_rgba(color)

    if darker < 0:
        return tuple_rgb

    out = (
        (tuple_rgb[0] * (1 - darker) ),
        (tuple_rgb[1] * (1 - darker) ),
        (tuple_rgb[2] * (1 - darker) ),
        tuple_rgb[3],
    )
    return mplcolors.to_hex(out)


def txt_color(color) -> str:
    """

    Find a text color adapted to the contrast

    """
    tuple_rgb = mplcolors.to_rgba(color)

    avg = (tuple_rgb[0] + tuple_rgb[1] + tuple_rgb[2]) / 3

    txt_color = "#000000"
    if avg < 0.5:
        txt_color = "#ffffff"
        print(tuple_rgb, avg)
    return txt_color


def find_color(node, color_filter):
    color = "grey"

    for key in color_filter:
        if key in node:
            color = color_filter[key]
    return mplcolors.to_hex(color)



def colorscale(
    lvl: float,
    min_lvl: float,
    max_lvl: float,
    color_map: str = "rainbow_PuRd",
    log_scale: bool = True,
) -> tuple:
    """
    Returns the rgb color according to the lvl of the color scale

    Args:
        lvl (float): Lvl of the current node
        min_lvl (float): Lower bound
        max_lvl (float): Upper bound
        color_map (str): Name of the Paul Tol's color map desired
        log_scale (bool): Choose either log scale or not

    Returns:
        color (tuple): rgb tuple for the color
    """
    if lvl is None:
        return (0.5,0.5,0.5) # Grey
    cmap = tol_cmap(color_map)

    lvl = max(lvl,min_lvl)
    lvl = min(lvl,max_lvl)
     
    if log_scale:
        min_lvl = log10(min_lvl)
        max_lvl = log10(max_lvl)
        lvl = log10(lvl)

    scale = (cmap.__dict__["N"] * (lvl - min_lvl)) / (max_lvl - min_lvl)
    color = cmap(round(scale))
    color = (color[0], color[1], color[2])
    return color

def colorscale_legend(
        min_lvl: float,
        max_lvl: float,
        color_map: str = "rainbow_PuRd",
        log_scale: bool = False,
        levels:int=None
    ):
    

    if levels is None:
        levels = max_lvl-min_lvl+1

    # Used for ratio values (0 -> 1), now have 10 values instead of just 0 and 1
    if max_lvl == 1:
        levels = 10 
    
    ref_vals = [None] + list(np.linspace(min_lvl,max_lvl,levels))
    ref_names = [str(item) for item in ref_vals]
    ref_names[1:] = [str(round(item,1)) for item in ref_vals[1:]]
    if log_scale:
        ref_vals = [None] + list(np.logspace(log10(min_lvl),log10(max_lvl),levels))
        ref_names[1:] = [str(round(item,1)) for item in ref_vals[1:]]
    
    scale ={name_:colorscale_hex(val_,min_lvl,max_lvl,color_map,log_scale=log_scale) for name_,val_ in zip(ref_names,ref_vals)}
    return scale

def colorscale_hex(*args, **kwargs) -> str:
    """
    Returns the rgb color according to the lvl of the color scale

    Args:
        lvl (float): Lvl of the current node
        min_lvl (float): Lower bound
        max_lvl (float): Upper bound
        color_map (str): Name of the Paul Tol's color map desired
        log_scale (bool): Choose either log scale or not

    Returns:
        color (tuple): rgb tuple for the color
    """
    return mplcolors.to_hex(colorscale(*args,**kwargs))
    
