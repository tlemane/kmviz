# Deploy a **kmviz** instance

This page describes how to deploy an instance of **kmviz** along with a **kmindex server** and a **MySQL DB** for metadata using `docker compose`, and [:fontawesome-brands-docker: tlemane/kmviz](https://hub.docker.com/r/tlemane/kmviz), [:fontawesome-brands-docker: tlemane/kmindex](https://hub.docker.com/r/tlemane/kmindex), [:fontawesome-brands-docker: mysql/mysql-server](https://hub.docker.com/r/mysql/mysql-server) docker images.

## 0. Index construction

This guide does not describe how to build an index. See [index construction](https://tlemane.github.io/kmindex/construction/) for instructions.

For the example, we assume that the index was built using: `kmindex build -i kmindex_directory/global_index -r index_1 -d kmindex_directory/index_1_directory ...`.

A **kmindex** index is a directory composed of one json file, `index.json`, and one or more symlinks for each registered sub-index. According to the previous command, we have one index `index_1` registered in the global index `global_index`, as illustrated below.

``` title="kmindex_directory structure"
kmindex_directory
├── global_index
│   ├── index_1 -> /path/to/kmindex_directory/index_1_directory
│   └── index.json
└── index_1_directory
```

## 1. The `kmindex-service`

The `kmindex-service` is a docker container that runs a `kmindex-server` instance allowing to query `kmindex` indexes through HTTP requests.

```yaml title="kmindex-service"
services:
  kmindex-service:
    container_name: kmindex-service_cnt
    image: tlemane/kmindex:latest
    volumes:
      - ./kmindex_directory:/home/
    entrypoint: kmindex-server
    command: "--index /home/global_index -a 0.0.0.0 --port 8080 -d /home/kmindex_logs"
    ports:
      - "8080:8080"
```

### Patch the index

The index produced by `kmindex` requires small patches to be used in this configuration. These patches can be applied using the following script.

```bash title="patch_index.sh"
#!/usr/bin/env bash

index_path=$1
new_path_prefix="/home"

indexes=$(ls --ignore=index.json ${index_path})

for index in ${indexes}
do
    path=$(realpath ${index_path}/${index})
    base=$(basename ${path})
    rm ${index_path}/${index}
    ln -s ${new_path_prefix}/${base} ${index_path}/${index}
done

new_index_path=${new_path_prefix}/$(basename ${index_path})

jq --arg new_index_path "$new_index_path" '.path = $new_index_path' ${index_path}/index.json > tmp.json
mv tmp.json ${index_path}/index.json
```

```bash
bash patch_index.sh kmindex_directory/global_index
```

??? "About the patches"
    ### Fix symlinks

    A `kmindex` index is a directory composed of one json file, `index.json`, and one or more symlink pointing to the index directories. In the example, only one sub-index `index_1` is registered. Within the docker, `kmindex_directory` is mounted at `/home/`. As a result, the symlink `global_index/index_1` should point to the index directory `/home/index_1_directory`

    ``` title="kmindex_directory structure"
    kmindex_directory
    ├── index
    │   ├── index_1 -> /path/to/kmindex_directory/index_1_directory
    │   └── index.json
    └── index_1_directory
    ```


    ### Fix json index path

    The `index.json` file contains an absolute path to its parent directory, *e.g.* `"path": "<prefix>/kmindex_directory/index"`. This field should be replaced with `"path": "/home/<directory_name>"`.



## 2. The `metadata-service`

The `metadata-service` is a docker container that runs a `mysql` server. In this example, the we assume a database `mydb` containing a `mytable` table. The db is created by `init.sql` instructions on the first container run.

```yaml title="metadata-service"
services:
  metadata-service:
    container_name: metadata-service_cnt
    image: mysql/mysql-server
    environment:
      MYSQL_ROOT_PASSWORD: kmviz_password
      MYSQL_ROOT_HOST: '%'
    volumes:
      - mysql-storage:/var/lib/mysql
      - init.sql:/home/init.sql            # Instructions to create the db and the table
    command: "--init-file /home/init.sql"
    ports:
      - "3036:3036"

# Create a /var/lib/docker/volumes/mysql-storage on the host to
# store the db data in a persistent way.
# 'docker compose down' will not remove the volume
# Use 'docker compose down -v' to delete the volume (and data)
volumes:
  - mysql-storage:
```

## 3. The `kmviz-service`

The `kmviz-service` is a docker container that runs the **kmviz** web service. It depends on the previous services `kmindex-service` and `metadata-service`.

```yaml title="kmviz-service"
services:
  kmviz:
    image: tlemane/kmviz:latest
    volumes:
      - ./kmviz_directory:/home/
    depends_on:
      - kmindex-service
      - metadata-service
    command: "-w 1 -b 0.0.0.0:5000"
    ports:
      - "5000:5000"
```

```toml title="kmviz_directory/config.toml"
[databases]

[databases.TARA]
type = "kmindex-server"
[databases.TARA.params]
url = "kmindex-service"
port = 8080
[databases.TARA.metadata]
type = "mysql"
[databases.TARA.metadata.params]
host = "metadata-service"
database = "mydb"
user = "root"
password = "kmviz_example"
idx = "ID"
table = "mytable"
geodata = { latitude = "Lat", longitude = "Long"}

[cache]

[cache.serverside]
type = "disk"
params.cache_dir = ".results/kmviz_serverside_cache"
params.threshold = 0
params.default_timeout = 86400

[cache.manager]
type = "disk"
params.directory = ".results/kmviz_manager_cache"

[cache.result]
type = "disk"
params.cache_dir = ".results/kmviz_result_cache"
params.threshold = 0
params.default_timeout = 1209600
```

## 4. Start the service

``` title="Final directory structure"
compose.yml
kmindex_directory
├── global_index
│   ├── index_1 -> /home/index_1
│   └── index.json
└── index_1
kmviz_directory
└── config.toml
```

```yaml title="compose.yml"
services:
  kmindex-service:
    image: tlemane/kmindex:latest
    volumes:
      - ./kmindex_directory:/home/
    entrypoint: kmindex-server
    command: "--index /home/index -a 0.0.0.0 --port 8080 -d /home/kmindex_logs"
    ports:
      - "8080:8080"

  metadata-service:
    image: mysql/mysql-server
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_ROOT_HOST: '%'
    volumes:
      - mysql-storage:/var/lib/mysql
      - init.sql:/home/init.sql
    command: "--init-file /home/init.sql"
    ports:
      - "3036:3036"

  kmviz-service:
    image: tlemane/kmviz:latest
    volumes:
      - ./kmviz_directory:/home/
    depends_on:
      - kmindex-service
      - metadata-service
    command: "-w 1 -b 0.0.0.0:5000"
    ports:
      - "5000:5000"

volumes:
  mysql-storage:
```

```bash title="Start the service and detach"
docker compose up -d
```

The **kmviz** instance is now available at `localhost:5000`.

## Appendix

### Appendix: Load a kmindex plugin

The default docker image does not contain any plugins. To install and use plugins, we create a new docker image based on `tlemane/kmviz` as described below.

```yaml title="compose.yml"
services:
  kmviz-service:
    build:
      context: ./kmviz_docker
      dockerfile: Dockerfile
    volumes:
      - ./kmviz_directory:/home/
    depends_on:
      - kmindex-service
      - metadata-service
    command: "-w 1 -b 0.0.0.0:5000"
    ports:
      - "5000:5000"

volumes:
  mysql-storage:
```

```docker title="kmviz_docker/Dockerfile"
FROM tlemane/kmviz:latest

RUN apt-get install -y git
ENV PIP_SRC=/opt/
RUN pip install -e "git+https://github.com/tlemane/kmviz.git#subdirectory=plugins/kmviz_instance_plugin&egg=kmviz_instance_plugin"
```

```toml title="kmviz_directory/config.toml"
[plugins.kmviz_instance_plugin]
```

### Appendix: Use [Redis](https://redis.io/fr/) caching

```yaml title="compose.yml"
services:
  redis-service:
    image: redis:alpine
    ports:
      - "6379:6379"

  kmviz-service:
    image: tlemane/kmviz:latest
    volumes:
      - ./kmviz_directory:/home/
    depends_on:
      - kmindex-service
      - metadata-service
      - redis-service
    command: "-w 1 -b 0.0.0.0:5000"
    ports:
      - "5000:5000"

volumes:
  mysql-storage:
```

```toml title="kmviz_directory/config.toml"
[databases]

[databases.TARA]
type = "kmindex-server"
[databases.TARA.params]
url = "kmindex-service"
port = 8080
[databases.TARA.metadata]
type = "mysql"
[databases.TARA.metadata.params]
host = "metadata-service"
database = "mydb"
user = "root"
password = "kmviz_example"
idx = "ID"
table = "mytable"
geodata = { latitude = "Lat", longitude = "Long"}

[cache]

[cache.serverside]
type = "redis"
params.host = "redis-service"
params.db = 0

[cache.manager]
type = "disk"
params.directory = ".results/kmviz_manager_cache"

[cache.result]
type = "redis"
params.host = "redis-service"
params.db = 1
```

### Appendix: Load balancing

See [Compose Deploy Specification](https://docs.docker.com/compose/compose-file/deploy/)

```yaml title="compose.yml"
services:
  kmindex-service:
    image: tlemane/kmindex:latest
    volumes:
      - ./kmindex_directory:/home/
    entrypoint: kmindex-server
    command: "--index /home/index -a 0.0.0.0 --port 8080 -d /home/kmindex_logs"
    expose:
      - 8080
    deploy:
      replicas: 3
      endpoint_mode: dnsrr
```

### Appendix: Analytics with [Matomo]()

:warning: Requires `kmviz`>=`v0.3.2`

#### Create the `matomo` service

```yaml title="compose.yml"
services:
  matomo:
    image: matomo
    volumes:
      - matomo:/var/www/html:z
    environment:
      - MATOMO_DATABASE_HOST=matomo
      - MYSQL_PASSWORD=password
      - MYSQL_DATABASE=matomo
      - MYSQL_USER=root
      - MATOMO_DATABASE_ADAPTER=mysql
      - MATOMO_DATABASE_TABLES_PREFIX=matomo_
      - MATOMO_DATABASE_USERNAME=root
      - MATOMO_DATABASE_PASSWORD=password
      - MATOMO_DATABASE_DBNAME=matomo
    depends_on:
      - metadata-service
    expose:
      - 80
    ports:
      - 8040:80

volumes:
  mysql-storage:
  matomo:
```

Note that we use the database hosted by `metadata-service` to store the `matomo` tables.

Because `matomo` does not support headless setup, you have to run the instance to follow the setup wizard.

1. `docker compose up metadata-service matomo`
2. Go to `localhost:8040` and follow the setup. For the `kmviz` url, use `http/localhost:8090`.
3. Copy the js tag provided by `matomo` and put in `kmviz_directory/template.html`, as described below.

```html title="kmviz_directory/template.html"
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
        <script>
          var _paq = window._paq = window._paq || [];
          _paq.push(['trackPageView']);
          _paq.push(['enableLinkTracking']);
          (function() {
            var u="//localhost:8040/";
            _paq.push(['setTrackerUrl', u+'matomo.php']);
            _paq.push(['setSiteId', '1']);
            var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
            g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
          })();
        </script>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
```
4. Update the `kmviz_directory/config.toml` to pass the html template, as described below.
```toml title="kmviz_directory/config.toml"
[html]
template = "/home/template.html"
```
5. Start all the services and finalize the tracking configuration in `matomo`.


## Self-contained example

A self-contained example is available here: [self.tar.bz2](https://raw.githubusercontent.com/tlemane/kmviz/main/tests/deploy_example/self.tar.bz2).

```bash
wget https://raw.githubusercontent.com/tlemane/kmviz/main/tests/deploy_example/self.tar.bz2
tar jxvf self.tar.bz2
cd self
docker compose up
```

