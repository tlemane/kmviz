# Metadata

|Method|Route|Header|
|---|---|---|
|`POST`|`<url>/api/query/<database_name>`|(`Content-Type`: `multipart/form-data`)|

**Form options**

* `<option_name>`: database option
* `fastx`: Fasta or Fastq file

!!! Warning
    `<url>/api/query/<database_name>` is the default route, but this may vary depending on the **kmviz** instance.

!!! Tip
    The response is a ZIP archive containing a TSV for each sequence query. The name of the file is a **kmviz** session ID, which can be used to load the results on the corresponding instance. See X for more details.

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
    $ python -m kmviz api --url http://localhost --port 8050 metadata --database ExampleDB --opt z 2 --fastx query.fa
    [kmviz:116f8d28] ~ 2024-07-21 13:35:27.000 ~ INFO ~ url=http://localhost, port=8050, auth=None
    [kmviz:116f8d28] ~ 2024-07-21 13:35:27.231 ~ INFO ~ POST http://localhost:8050/api/query/ExampleDB -> status 200
    [kmviz:116f8d28] ~ 2024-07-21 13:35:27.232 ~ INFO ~ kmviz-c36bda10-1f44-4154-82ca-978ba3e3c286.zip
    ```

=== "Using cURL"
    <!-- termynal -->
    ```
    $ curl -O -J -X POST -F'z=2' -F 'fastx=@./query.fa' http://localhost:8050/api/query/ExampleDB
    kmviz-c36bda10-1f44-4154-82ca-978ba3e3c286.zip
    ```

**Response**
<!-- termynal -->
```bash
$ unzip kmviz-c36bda10-1f44-4154-82ca-978ba3e3c286.zip
Archive:  kmviz-c36bda10-1f44-4154-82ca-978ba3e3c286.zip
  extracting: Query_0.tsv
  extracting: Query_1.tsv
$ head -n 4 Query_0.tsv
ID      CovXK   CovXB   CovYK   CovYB   Depth   Lat     Long    SSD     Temp    Salinity        Chl_a   O2      NO3 NO2      NH4     Fe      Phos    Si      Month   biome   T_woa   ampl_woa        sd_T_woa
6DCM    0.957   0.691   1.471   1.423   DCM     36.5229 -4.0023 731                     55.2985         0.073991253 0.030633541      0.017879906     0.001383199     0.12475 1.71925 9       temperate       18.164  10.954  4.02955971728321
9DCM    0.8     0.577   1.257   1.199   DCM     39.1633 5.916   714     14.7076 25.6379 29.4855 75.0    0.01675451  0.048709321      0.015086659     0.00138773                      9       temperate       18.4135 10.808  4.11925075104685
11DCM   0.186   0.134   0.186   0.263   DCM     41.6686 2.7996  697                                     0.024274436 0.031807316      0.009132409     0.001387775                     10      temperate       16.7145 8.745   3.43239780575762
```
