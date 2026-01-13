"""Owega Functions init."""
from . import longTermSouvenirs as lts
# from .longTermSouvenirs import LTS, setAdd, setDel, setEdit
from .functions import Functions
# from .imageGen import ImageGenerators
from .utility import Utility
from ..config import baseConf

existingFunctions = (
    Functions()
    .append(Utility, 'utility')
    .append(lts.LTS, 'lts')
    # should not be hardcoded into the system, to remove:
    # .append(ImageGenerators, 'imagegen')
)
existingFunctions.disableGroup('lts')


def connectLTS(addfun, delfun, editfun) -> None:
    """Connect Long-Term-Souvenir functions."""
    lts.setAdd(addfun)
    lts.setDel(delfun)
    lts.setEdit(editfun)
    if baseConf.get("lts_enabled", False):
        existingFunctions.enableGroup('lts')
    else:
        existingFunctions.disableGroup('lts')


def function_to_tool(fun) -> dict:
    """Convert an old function to a tool."""
    dct = {"type": "function", "function": fun}
    return dct


def functionlist_to_toollist(fun_lst) -> list:
    """Convert old functions as tools."""
    tool_lst = []
    for fun in fun_lst:
        tool_lst.append(function_to_tool(fun))
    return tool_lst


__all__ = [
    'lts',
    'Functions',
    'Utility',
    # 'ImageGenerators',
    'existingFunctions',
    'connectLTS',
    'function_to_tool',
    'functionlist_to_toollist',
]
