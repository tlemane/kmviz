# Database mode

The **kmviz** interface is divided into 4 major areas:

1. **Input**
2. **Database/Query selector**
3. **Tab selector**
4. **Main window**

<img src="../assets/home_paint.png", class="ImageHelp">

## 1.Input

### Select database(s)

**kmviz** will send the query to the selected databases.

<img src="../assets/input_db_select.png", class="ImageHelp">

For each selected databases, you can change the configuration. In this example, `DB` uses `kmindex-server` which allows two query options: `z` and `coverage`. For details see [kmindex documentation](https://tlemane.github.io/kmindex/server-query/#accessing-index-information).

Providers can provide various types of options, see [User options](../configuration/user_options.md)

<img src="../assets/db_config.png", class="ImageHelp">

### Import query

The query sequence(s) should be provided in Fasta/Fastq format, by copy-pasting or directly importing a file. The fastx identifiers are used as query id in the results.

When submitting a query, you receive a unique session id that can be used later to reload your results without query the databases again. The session id is a 42 characters string that matches `kmviz-[a-fA-Z1-9]{8}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{12}`, *e.g.* `kmviz-1fb396fd-96f2-45ba-bd78-fd23fde9921e`.

The 3 import layouts, `file`, `text` and `session` are illustrated below.


<div class="grid cards" markdown>

<img src="../assets/input_text.png", class="ImageHelp">

<img src="../assets/input_file.png", class="ImageHelp">

<img src="../assets/input_session.png", class="ImageHelp">

</div>

### Submit

The `Submit` button triggers the query and pops up a notification, as shown below, with your session id.

<img src="../assets/notif.png", class="ImageHelp">

The `Reset` button simply reloads the page to perform a new query.

## 2. Database/Query selector

<img src="../assets/query.png", class="ImageHelp">

**kmviz** can display results for **only one pair of database/query** at a time. Database and query are selectable using these two dropdown selectors located at the top right corner.

!!! tip "Important"
    The `json` button allows to download all the results in a `json`. Use this file to explore your results later using a local [**kmviz instance**](session.md). This allows to reduce the server workload for multi-user instances.

The blue switch allows to enable *auto update* on maps and plots. For details see [this section](#figures).

## 3. Tab selector

<img src="../assets/tabs.png", class="ImageHelp">

- **Index**: Display information about the selected database
- **Table**: A table of metadata corresponding to the selected database/query
- **Map**: Make maps from selected metadata
- **Plot**: Make plots from selected metadata
- **Sequence**: Display query coverage for a pair sample/query
- **Help**: Help page

When a plugin provides a new layout, it appears as a new tab. See [layout plugin](../plugins/plugin_layout.md).

## 4. Main

### Index tab

The `Index` tab shows information about the index selected by the [Database selector](#2-databasequery-selector):

* The top table contains various index information, *e.g.* number of samples, version, etc.
* The bottom table corresponds the complete metadata table.

<img src="../assets/index_tab.png", class="ImageHelp">

### Table tab

The `Table` tab shows a sub-table of metadata corresponding to the hits for the query selected by the [Query selector](#2-databasequery-selector).

!!! tip "Important"
    **These data are used to make all the representations, *e.g.* maps, which means that a filter applied on the table will be reflected on the figures. Note that this works both ways: selecting some points on the map will be reflected on the table.**

<img src="../assets/table_tab.png", class="ImageHelp">

### Sequence tab

The `Sequence` tab shows a plot representing the query coverage for a pair of a `Query` and a `Sample`. The `Query` is selected by the [Query selector](#2-databasequery-selector) while the `Sample` selector is available at the top of the tab.

!!! note
    Click on a point on the map or the plot jumps to the `Sequence` tab and shows a coverage plot corresponding the selected point.

<img src="../assets/sequence_tab.png", class="ImageHelp">

### Help tab

Simply links to the documentation. Also displays plugin-specific help, when applicable, i.e. when some plugins are loaded and provide additional help.

### Figures

Maps and plots are produced using [plotly](https://plotly.com/python/) and we follow the naming of plot properties. This means that you can follow the plotly documentation to learn more about each available property. The documentation links for each map and plot types supported by **kmviz** are provided in next sections [Maps](#map-tab) and [Plots](#plot-tab).

When making figures, there are 2 types of action: those that **create a new figure** (`Map` tab for maps and `Trace` tab for plots), *e.g.* change the plot type, and those that **update the figure**, *e.g.* change the title. The blue switch (see [Query selector](#2-databasequery-selector)) at the top right corner allows to enabled/disabled the auto updates. When enabled, all properties corresponding to **update actions** are automatically applied when the figure is modified. For example, if you set a title, then change the plot type, the title remains. When disabled, changing a property value only triggers a change for this property.

This part of the documentation is still under construction. Below are a few documentation links and screenshots. The best way to learn how to use the interface is probably to play with the [Plot-Only](plot_only.md) mode.

#### Map Tab

<img src="../assets/map_ex.png", class="ImageHelp">

*Documentation links*: [Map](https://plotly.com/python-api-reference/generated/plotly.express.scatter_geo)

#### Plot Tab

<img src="../assets/plot_ex.png", class="ImageHelp">

*Documentation links*: [Scatter](https://plotly.com/python-api-reference/generated/plotly.express.scatter), [Line](https://plotly.com/python-api-reference/generated/plotly.express.line), [Area](https://plotly.com/python-api-reference/generated/plotly.express.area), [Bar](https://plotly.com/python-api-reference/generated/plotly.express.bar), [Parallel categories](https://plotly.com/python-api-reference/generated/plotly.express.parallel_categories), [Parallel coordinates](https://plotly.com/python-api-reference/generated/plotly.express.parallel_coordinates), [Scatter matrix](https://plotly.com/python-api-reference/generated/plotly.express.scatter_matrix), [Density heatmap](https://plotly.com/python-api-reference/generated/plotly.express.density_heatmap), [Density contour](https://plotly.com/python-api-reference/generated/plotly.express.density_contour), [Violin](https://plotly.com/python-api-reference/generated/plotly.express.violin), [Box](https://plotly.com/python-api-reference/generated/plotly.express.box)
