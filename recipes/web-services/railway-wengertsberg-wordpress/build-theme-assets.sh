#!/bin/sh
set -eu

theme_dir=${1:?Theme directory required}
mkdir -p "$theme_dir/assets"
for file in style.css site.js share-preview.png design-preview.css design-preview.js; do
    digest=$(sha256sum "$theme_dir/$file" | cut -c1-12)
    stem=${file%.*}
    extension=${file##*.}
    cp "$theme_dir/$file" "$theme_dir/assets/$stem.$digest.$extension"
done
