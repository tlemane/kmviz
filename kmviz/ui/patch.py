from typing import Union, List, Any

from dash import Patch

def make_patch(*paths):
    p = Patch()
    for path in paths:
        p = p[path]
    return p

def patch_paths_from_id(id: Union[dict, str]) -> List[str]:
    if isinstance(id, str):
        paths = id.split("-")[-1].split("_")
    else:
        paths = id["index"].split("_")

    if len(paths) > 1:
        return paths[:-1], paths[-1]

    return None, paths[0]

def patch_value(patch: Patch, key: str, value: Any):
    patch[key] = value
    return patch

def patch_value_id(patch: Patch, id: Union[dict, str], value: Any):
    paths, key = patch_paths_from_id(id)

    if paths:
        for p in paths:
            patch = patch[p]

    return patch_value(patch, key, value)

def style_hide_patch():
    patch = Patch()
    patch["display"] = "none"
    return patch

def style_inline_patch():
    patch = Patch()
    patch["display"] = "inline"
    return patch
