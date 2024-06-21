---
hide:
  - navigation
---

# Welcome to **kmviz** documentation!

:warning: **kmviz** is a work in progress :warning:

**kmviz** is a user-friendly web interface for interacting with biological sequence indexes. In a nutshell, it connects to multiple, local or distant, sequence indexes to performs sequence queries. Results can then be explored through *`tables`*, *`plots`*, *`sequence views`*, or even *`maps`* when metadata contains geographical information. Note that representations are fully customizable allowing to make production-grade figures as illustrated below.


Before installing and playing with **kmviz**, let's quickly introduce the **kmviz** vocabulary.

* `Query` refers to a pair `id`:`sequence`.
* `Provider` refers to an index engine, *e.g.* one capable of querying a kmindex db.
* `MetaDB` refers to a db engine, *e.g.* one capable of load and query `.tsv` files.
* `Database` refers to a pair of configured `Provider`/`MetaDB`.

In short, you select one or more `Databases`, you provide one or more `Queries`. For each `Database` and `Query`, the `Provider` responds with a list of identifiers matching your `Query`, and the `MetaDB` returns the metadata associated with these identifiers to finally serves them into the interface.

!!! info "Contact"
    Teo Lemane: teo[dot]lemane[at]genoscope[dot]cns[dot]fr
