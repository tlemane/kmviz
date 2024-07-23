# Table Tab

The `Table` tab shows a metadata table corresponding to the hits for the query selected by the [Query selector](./nav.md#selectors). In other words, it is a sub-table of the complete metadata table displayed in the `Index` table.

<img src="../../assets/table/table.png", class="ImageHelp" width="90%">

!!! Note
    In addition to the metadata, some columns correspond to query coverage metrics:

    - `CovXK`: proportion of positive *k*-mers
    - `CovXB`: proportion of bases covered by at least a positive *k*-mer
    - `CovYK`: mean abundance per *k*-mer
    - `CovYB`: mean abundance per base

    Note that `CovYK` and `CovYB` are optional and only present when the underlying `Provider` supports abundance queries.

---

Each column supports filtering and sorting. Available filters may vary depending on the data type of the column.

<img src="../../assets/table/filtercol.png", class="ImageHelp" width="20%">

---

At the top, you can apply filters using [SQL `WHERE` clause syntax](https://www.w3schools.com/sql/sql_where.asp), *e.g.* `Temp > 20 and CovXK between 0.5 and 0.8 and ID like '%DCM'`. To apply it, use the first button on the right or press `Enter`. The second button allows to remove the filters.

<img src="../../assets/table/filtersql.png", class="ImageHelp" width="90%">

---

!!! tip "Important"
    This table is used to make all the representations, *e.g.* maps, which means that a filter applied on the table will be reflected on the figures. Note that this works both ways: selecting some points on the map will be reflected on the table, and therefore on the plot too.


