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

echo "Exporting environment variables..."
export FTP_SERVER_NAME_IGC="95.215.226.140"
export FTP_LOGIN_IGC="netcoupe_ludoigc"
export FTP_PASSWORD_IGC="IGC2020Sw7qo"
export FTP_SERVER_NAME_HEATMAP="ftp3.phpnet.org"
export FTP_LOGIN_HEATMAP="netcoupe_DG800ludo"
export FTP_PASSWORD_HEATMAP="SIx4m8nu_"
export API_KEY="dg808b-8-219-b-133"

cd ./release