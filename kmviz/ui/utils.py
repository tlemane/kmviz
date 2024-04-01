from typing import List, Dict
from dash.exceptions import PreventUpdate

def prevent_update_on_none(*values):
    if any(value is None for value in values):
            raise PreventUpdate()

def prevent_update_on_empty(*values):
    prevent_update_on_none(*values)
    if any(not len(value) for value in values):
        raise PreventUpdate()

def make_select_data(values: List[str]) -> Dict[str, str]:
    return [{ "label": x, "value": x } for x in values]
