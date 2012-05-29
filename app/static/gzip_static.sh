#!/bin/bash
#
# This script pre-gzips static files for quick use by the webserver
#

# Add all file extensions which you want pre-gzipped
FILETYPES=( css js )

# Start processing
for EXT in ${FILETYPES[@]}; do
    echo
    echo "gzipping '$EXT' files...";

    # Find files in directories except twitter-bootstrap
    FILES=$( find . -name "*twitter-bootstrap*" -prune -o -name "*.$EXT" -print )

    # Find files inside ./twitter-bootstrap/bootstrap
    FILES2=$( find ./twitter-bootstrap/bootstrap -name *.$EXT -print )

    # Process files
    for file in $FILES $FILES2; do
        echo "$file > $file.gz"
        #gzip -c $file > $file.gz
    done
done
