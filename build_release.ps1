
Remove-Item ./release/* -recurse -force
# Copy Python source code
copy-item ./*.py .\release\

copy-item ./app.yaml .\release\
copy-item ./requirements.txt .\release\
copy-item ./static	./release\ -Recurse

# Copy igc_lib
$exclude = @('requirements.txt', 'main.py', 'main_local.py',  'LICENSE', 'README.md', '.gitignore', '*.pyproj')
copy-Item ../igc_lib/* ./release -Recurse -Force -Exclude $exclude

Remove-Item ./release/.git -recurse -force
Remove-Item ./release/.vscode -recurse -force
Remove-Item ./release/__pycache__ -recurse -force
Remove-Item ./release/lib/__pycache__ -recurse -force
