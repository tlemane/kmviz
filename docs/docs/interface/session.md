# Session mode

**kmviz** supports a `session` mode that allows loading a session JSON file obtained via the [API](../api/session.md) or downloaded from another [**kmviz** instance](../interface/database.md#2-databasequery-selector).

The `session` mode does not require any configuration and can be started as follows:

```bash
python -m kmviz app start session
```

An upload button is available at the top, otherwise the interface is the same as the database interface, but without the sidebar.

<img src="../assets/session.png", class="ImageBorder">


