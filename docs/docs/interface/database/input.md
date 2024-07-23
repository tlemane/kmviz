# Input

## Database(s)

### Selection

In **kmviz** a `Database` refers to a pair of one `Provider`, i.e. a sequence index, and a `MetaDB`, i.e. a store that associate metadata to the samples indexed by the `Provider`. Before submitting your query, you have to select one or more `Database(s)`.

<img src="../../assets/input/database.png", class="ImageHelp" width="25%">

After selecting a `Database`, its configuration becomes available.

### Configuration

<img src="../../assets/input/configuration.png", class="ImageHelp" width="25%">

In this example, `ExampleDB` uses `kmindex-server` which has two query options: `z` and `coverage`. For more details see [kmindex documentation](https://tlemane.github.io/kmindex/server-query/#accessing-index-information)

Note that all options are not always displayed. When hosting an instance, one can decide to fix (and hide) some options.

## Sequence(s)

**kmviz** supports sequence(s) in `FASTA` or `FASTQ` format from raw text or file.

<div class="grid cards" markdown>

<img src="../../assets/input/text.png", class="ImageHelp" width="40%">

<img src="../../assets/input/file.png", class="ImageHelp" width="40%">

</div>

## Session

After submitting a query, you receive a unique `session-id` that can be used to reload your results later. The `session-id` is a 42 characters string that matches `kmviz-[a-fA-Z1-9]{8}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{4}-[a-fA-Z1-9]{12}`, *e.g.* `kmviz-1fb396fd-96f2-45ba-bd78-fd23fde9921e`.

<img src="../../assets/input/session.png", class="ImageHelp" width="25%">

