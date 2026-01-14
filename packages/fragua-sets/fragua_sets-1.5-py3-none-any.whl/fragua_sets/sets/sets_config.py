"""Configuration for Sets."""

from typing import Any, Dict, List
from fragua import FraguaSet

from fragua_sets.functions.extraction import EXTRACTION_FUNCTIONS
from fragua_sets.functions.loading import LOADING_FUNCTIONS
from fragua_sets.functions.transformation import TRANSFORMATION_FUNCTIONS
from fragua_sets.functions.utility import UTILITY_FUNCTIONS

FUNCTION_LISTS: Dict[str, Dict[str, Any]] = {
    "extraction": {"functions": EXTRACTION_FUNCTIONS},
    "transformation": {"functions": TRANSFORMATION_FUNCTIONS},
    "loading": {"functions": LOADING_FUNCTIONS},
    "utility": {"functions": UTILITY_FUNCTIONS, "step_enabled": False},
}


def create_sets() -> List[FraguaSet]:
    """Create a list of FraguaSet objects from FUNCTION_LISTS."""
    sets_list: List[FraguaSet] = []

    for set_name, items in FUNCTION_LISTS.items():
        functions = items.get("functions", [])
        func_dict = {}

        for idx, func in enumerate(functions, start=1):
            func_name = getattr(func, "__name__", f"{set_name}_func_{idx}")
            if func_name == "<lambda>":
                func_name = f"{set_name}_lambda_{idx}"
            func_dict[func_name] = func

        func_set = FraguaSet(
            name=set_name,
            items=func_dict,
            step_enabled=items.get("step_enabled", True),
        )
        sets_list.append(func_set)

    return sets_list


FRAGUA_SETS: List[FraguaSet] = create_sets()
