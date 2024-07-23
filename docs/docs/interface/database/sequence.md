# Sequence Tab

The `Sequence` Tab allows to visiualize the coverage along a query and proposes two different views.

<img src="../../assets/sequence/select.png", class="ImageHelp" width="30%">


The coverage view is only available for a pair `Query`/`Sample`. The `Sample` selector is placed close to top navigation bar.

The `JSON` button allows to download a file containing the coverage information as presence/absence or abundance arrays. Note that it contains all coverage information corresponding to the selected `Query`, and not only the coverage of the selected `Sample`.

!!! note
    Click on a point on the map or the plot jumps to the `Sequence` tab and shows figures corresponding the selected point.

## Graph view

The `Graph` view plots presence/absence or abundance of each *k*-mer/base along the query sequence. As maps and plots, an customization interface is provided below the figure.

<img src="../../assets/sequence/graph.png", class="ImageHelp" width="90%">

## Sequence view

The `Graph` view represents presence/absence or abundance of each *k*-mer/base along the query sequence through a highlighted text area. The min and max of the color range can be modified using the `MIN COLOR` and `MAX COLOR` color pickers.

<img src="../../assets/sequence/sequence.png", class="ImageHelp" width="60%">