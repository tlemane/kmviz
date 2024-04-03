import dash_ag_grid as dag
from typing import Union

def make_ag_grid(id: Union[str, dict],
                 grid_opt: dict={},
                 col_def: dict={},
                 csv_export: dict={},
                 **kwargs):

    default_params = {
        "columnSize": "autoSize",
        "className": "ag-theme-balham"
    }

    default_col = {
        "filter": True,
        "sortable": True,
        "floatingFilter": True
    }

    default_opt = {
        "suppressMenuHide": False,
        "animateRows": True,
        "pagination": True,
        "loadingOverlayComponent": "CustomLoadingOverlay",
        "loadingOverlayComponentParams": {
            "loadingMessage": "Waiting for results..."
        },
        "rowSelection": "single",
    }

    default_export = {
        "fileName": "data.tsv",
        "columnSeparator": "\t"
    }

    return dag.AgGrid(
        id=id,
        defaultColDef={**default_col, **col_def},
        dashGridOptions={**default_opt, **grid_opt},
        csvExportParams={**default_export, **csv_export},
        **{**default_params, **kwargs},
    )

