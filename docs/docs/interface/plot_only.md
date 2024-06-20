# Plot-Only mode

**kmviz** support a `plot-only` mode that allows to make maps and plots using arbitrary data from a file.

The `plot-only` mode does not require any configuration and can be started as follows:

```bash
python -m kmviz.app --plot-only
```

The left panel is used to import your data from a TSV file as illustrated below. You can then refer to the [Database mode](database.md) for the documentation of `Map` and `Plot` tabs. 

<img src="../assets/plot_only.png", class="ImageBorder">

|Field|Description|Required|
|---|---|---|
|Index|Index column name|:white_check_mark:|
|Separator|Column separator|:white_check_mark:|
|Longitude|Longitude colmun name, if applicable|:x:|
|Latitude|Latitude colmun name, if applicable|:x:|
