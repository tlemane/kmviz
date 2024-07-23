# Infos

|Method|Route|Header|
|---|---|---|
|`GET`|`<url>/api`|-|

!!! Warning
    `<url>/api` is the default route, but this may vary depending on the **kmviz** instance.

=== "Using kmviz CLI"
    <!-- termynal -->
    ```
    $ python -m kmviz api --url http://localhost --port 8050 infos > infos.json
    ```

=== "Using cURL"
    <!-- termynal -->
    ```
    $ curl -X GET http://localhost:8050/api > infos.json
    ```

```json title="infos.json"
{
  "database": {
    "ExampleDB": {
      "options": {
        "coverage": {
          "state": {
            "default": 0.7,
            "max": 1.0,
            "min": 0.0,
            "name": "coverage",
            "step": 0.05,
            "value": 0.1
          },
          "type": "float"
        },
        "z": {
          "state": {
            "default": 0,
            "max": 5,
            "min": 0,
            "name": "z",
            "step": 1,
            "value": 3
          },
          "type": "int"
        }
      }
    }
  },
  "input": {
    "alphabet": "all",
    "max_query": 4294967296,
    "max_query_size": 4294967296,
    "max_size": 4294967296
  }
}
```