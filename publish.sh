python -m build
# Remove all whl builds in the dist folder as we require building the c++ extension on target machines.
rm -r dist/*.whl
python -m twine upload dist/*.tar.gz
