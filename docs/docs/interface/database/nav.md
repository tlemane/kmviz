# Navigation and selection

## Navigation

<img src="../../assets/nav/tabs.png", class="ImageHelp">

The navbar allows to switch between tabs. A dedicated help page is available for each one.

Note that additionnal tabs can be provided by [plugins]().

## Selectors

<img src="../../assets/nav/only_selectors.png", class="ImageHelp">

**kmviz** can display results for **only one** pair of **`Database`**/**`Query`** at a time. For both, the selector is placed at the top right corner. The query names correspond to the FASTA/Q identifiers.

## Buttons

Two buttons are available at the top right corner.

<img src="../../assets/nav/only_buttons.png", class="ImageHelp">

The first one allows to enabled/disbaled figure auto updates. When making figures, **kmviz** distinguishes 2 types of action: those that **create a new figure** (the `Trace` tab for both maps and plots), *e.g.* change the plot type, and those that **update the figure**, *e.g.* change the title. The blue switch at the top right corner allows to enabled/disabled the auto updates. When enabled, all properties corresponding to **update actions** are automatically re-applied when the figure is modified. For example, if you set a title, then change the plot type, the title remains.

The second one allows to download all the results in a session `JSON` file. A `session file` can be loaded by any **kmviz** instance running in [`session mode`](../session.md).
