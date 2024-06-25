# Database mode

The **kmviz** interface is divided into 4 major areas:

1. **Input**
3. **Tab selector**
2. **Query selector**
4. **Main window**

<img src="../assets/home_paint.png", class="ImageHelp">

## 1.Input

### Select database(s)

:construction:

### Import query

The query sequence(s) should be provided in Fasta/Fastq format, by copy-pasting or directly importing a file. The fastx identifiers are used as query id in the results.

When submitting a query, you receive a unique session id that can be used later to reload your results without query the databases again. The session id is a X characters string that matches `kmviz-[a-fA-Z1-9]{8}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{12}`, *e.g.* `kmviz-1fb396fd-96f2-45ba-bd78-fd23fde9921e`.

The 3 import layouts, `file`, `text` and `session` are illustrated below.


<div class="grid cards" markdown>

<img src="../assets/input_text.png", class="ImageHelp">

<img src="../assets/input_file.png", class="ImageHelp">

<img src="../assets/input_session.png", class="ImageHelp">

</div>

## 2. Query selector

<img src="../assets/query.png", class="ImageHelp">

**kmviz** can display results for **only one pair of database/query** at a time. Database and query are selectable using these two dropdown selectors located at the top right corner.

The blue switch allows to enable *auto update* on maps and plots. For details see [this section](#making-production-grade-representation).

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

:construction:

### Table tab

:construction:

### Making production-grade representation

Maps and plots are produced using plotly and we follow the naming of all figure properties. This means that you can follow the plotly documentation to learn more about each available property. The documentation links for each map and plot types supported by **kmviz** are provided in next sections [Maps](#maps) and [Plots](#plots).

When making figures, there are 2 types of action: those that **create a new figure**, *e.g.* change the plot type, and those that **update the figure**, *e.g.* change the title. The blue switch (see [Query selector](#2-query-selector)) at the top right corner allows to enabled/disabled the auto updates. When enabled, all properties corresponding to **update actions** are automatically applied when the figure is modified. For example, if you set a title, then change the plot type, the title remains. When disabled, changing a property value only triggers a change for this property.

#### Maps

:construction:

#### Plots

:construction: