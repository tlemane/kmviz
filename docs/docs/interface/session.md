# Session mode

**kmviz** support a `session` mode that allows to load results from a `json` file (from the [API](../interface/rest.md) or download from another [kmviz interface](../interface/database.md#2-databasequery-selector)).

The `session` mode does not require any configuration and can be started as follows:

```bash
python -m kmviz.app --session
```

With the `session` mode, the sidebar is disabled and a `Upload session` button is available at the top of the page.

