# REST API

## Endpoints

### `GET /api`

#### Example with `curl`

```bash
curl -X GET http://localhost:8050/api > info.json
```

```json title="info.json"
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
            "value": 2
          },
          "type": "int"
        }
      }
    }
  },
  "input": {
    "alphabet": "dna",
    "max_query": 10,
    "max_query_size": 100,
    "max_size": 400
  }
}
```

### `POST /api/query` (`Content-Type`: `multipart/form-data`)

#### Form options

* `database`: The database to query
* `<database_name>-<option_name>`: The database options
* `fastx`: Fasta or Fastq file


#### Example with `curl`

```bash
curl -F "database=ExampleDB"
     -F "ExampleDB-z=2"
     -F "ExampleDB-coverage=0.3"
     -F "fastx=@/path/to/fastx" > session.json
```

The `session.json` file can be used to explore the results in a local **kmviz** instance, see [Session mode](../interface/session.md).
