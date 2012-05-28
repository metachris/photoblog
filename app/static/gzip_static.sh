#!/bin/bash
# gzips all static files (css, js)

FILETYPES=( css js )

for item in ${FILETYPES[@]}; do
    echo
    echo "Zipping '$item'...";
    for file in $( find ./ -name "*.$item"); do
        echo "$file > $file.gz"
        gzip -c $file > $file.gz
    done
done
