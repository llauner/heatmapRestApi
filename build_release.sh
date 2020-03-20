#! /bin/bash

echo "Remove old directory"
rm -rf ./release
mkdir ./release

echo "Copy Python source code"
cp ./*.py ./release/
cp ./app.yaml ./release
cp ./requirements.txt ./release
cp -R ./static	./release

echo "Copy igc_lib"
mkdir ./release/igc_lib
cp -R ../igc_lib/* ./release/igc_lib
echo "Remove unnecessary files from igc_lib"
rm ./release/igc_lib/requirements.txt
rm ./release/igc_lib/main.py
rm ./release/igc_lib/main_local.py
rm ./release/igc_lib/LICENSE
rm ./release/igc_lib/README.md
rm -rf ./release/igc_lib/.gitignore
rm ./release/igc_lib/*.pyproj
mv ./release/igc_lib/* ./release
rmdir ./release/igc_lib

echo "Remove unecessary items"
rm -rf ./release/.git
rm -rf ./release/.vscode
rm -rf ./release/__pycache__
rm -rf ./release/lib/__pycache__