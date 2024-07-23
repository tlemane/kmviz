# Map Tab

<img src="../../assets/figure/map.png", class="ImageHelp" width="80%">

Maps are made using [`plotly.express.scatter_geo`](https://plotly.com/python-api-reference/generated/plotly.express.scatter_geo).

!!! Tip "On click"
    Clicking on a point jumps into the `Sequence` Tab to display the query coverage corresponding to this sample

!!! Tip "On selection"
    Using `Box select` or `Lasso select` allows to select a subset of points. The selection filters the metadata table, i.e. it applies at global scope and is also reflected in the `Plot` tab.