import sys
from loguru import logger

def mmap_startlog(verbose):
    """
    Logging function of marauders map.
   
    """
    file = "maraudersmap.log"

    format_verbose = "<d><green>{elapsed}</green> : <level>{level}</level> - <blue>{file}:{function}:{line}</blue></d> - <level>{message}</level>"
    format_normal = "<level>{message}</level>"
    logger.remove()    
    if verbose:
        logger.add(sys.stdout, format=format_verbose,)
        logger.add(file, format=format_verbose, retention="1 day")
    else:
        logger.add(sys.stdout, format=format_normal, level="INFO",)
        logger.add(file, format=format_normal, level="INFO", retention="1 day")
    
    
    
    
        
   
