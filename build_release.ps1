
Remove-Item ./release/* -recurse -force
# Copy Python source code
copy-item ./*.py ./release/

copy-item ./app.yaml ./release/
copy-item ./requirements.txt ./release/
copy-item ./static	./release/ -Recurse

# Copy igc_lib
$exclude = @('requirements.txt', 'main.py', 'main_local.py',  'LICENSE', 'README.md', '.gitignore', '*.pyproj', 'trash.py', '*.pyc')
copy-Item ../igc_lib/*.py ./release -Recurse -Force -Exclude $exclude
copy-Item ../igc_lib/lib/* ./release/lib -Recurse -Force -Exclude $exclude

cd ./release/
