# Plot mode

**kmviz** support a `plot` mode that allows making maps and plots from arbitrary data (from `csv`,`tsv` or `xlsx`).

The `plot` mode does not require any configuration and can be started as follows:

```bash
python -m kmviz app start plot
```

Once a tsv file is loaded, the interface is the same as the database interface, but without the sidebar and `Index` and `Sequence` tabs.

<img src="../assets/plot_only.png", class="ImageBorder">

|Field|Description|Required|
|---|---|---|
|Index|Index column name|:white_check_mark:|
|Separator|Column separator|:white_check_mark:|
|Longitude|Longitude colmun name, if applicable|:x:|
|Latitude|Latitude colmun name, if applicable|:x:|
