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
