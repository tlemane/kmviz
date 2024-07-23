# Session

|Method|Route|Header|
|---|---|---|
|`POST`|`<url>/api/query`|(`Content-Type`: `multipart/form-data`)|

**Form options**

* `<database_name>#<option_name>`: database option
* `fastx`: Fasta or Fastq file

!!! Warning
    `<url>/api/query` is the default route, but this may vary depending on the **kmviz** instance.

**Query**
```title="Query.fa"
>Query_0
TGAACCTGGCAACTGGTGAAGAGACCGAAAGAATGGGAGATCCTAAGCCGCCACTCCTGGAGGACTAGCTCCGCCAGCGTGCGGATGCTATCCG
>Query_1
GCTTGCTTCCTACTTAGTTCCGCGCCCTCTGCGGCGTTGTCACTACATCCTGACATGTATCCGGCGAGATGAATTTTAATCTAGTGAGCCTCGT
```

=== "Using kmviz CLI"
    <!-- termynal -->
    ```
    $ python -m kmviz api --url http://localhost --port 8050 query --database ExampleDB --opt ExampleDB z 2 --fastx query.fa > session.json
    ```

=== "Using cURL"
    <!-- termynal -->
    ```
    $ curl -X POST -F'ExampleDB#z=2' -F 'fastx=@./query.fa' http://localhost:8050/api/query > session.json
    ```

The session file can then be explored using a local **kmviz** instance: `python -m kmviz app start session`. The interface is then available at `http://localhost:8050`. See [**kmviz** session mode](../interface/session.md) for more details.

