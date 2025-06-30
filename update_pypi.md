### How to update pypi SbfParser package ?

1) You will need `build`, `twine` and depending on your OS, `auditwheel`
```bash
pip install build twine auditwheel
```

2) Then, clean or creat `dist` folder
```bash
rm dist/*
```

3) You can now increment version in `pyproject.toml` and rebuild the project :
```bash
python3 -m build
```

4) If you have some files with `XXX-cp313-linux_x86_64.whl` in `dist` (for example `sbf_parser-1.0-cp313-cp313-linux_x86_64.whl`) you need to patch theses files, otherwise, you can directly go to 5.
```bash
auditwheel repair dist/sbf_parser-1.0.1-cp313-cp313-linux_x86_64.whl
```
Then you will obtain a file like `sbf_parser-1.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl`.
Delete the original `cpXXX-linux` file in `dist`, and copy the new one in the directory.
```bash
rm dist/sbf_parser-1.0-cp313-cp313-linux_x86_64.whl
cp wheelhouse/sbf_parser-1.0-cp313-cp313-manylinux2014_x86_64.manylinux_2_17_x86_64.whl dist/
```

5) Upload to pypi. You may need to have a pypi token.
```bash
python3 -m twine upload dist/*
```

### Test SbfParser package
Remove old venv,
rm -R venv
python -m venv venv
pip install sbf_parser
cd example
python3 decode.py

Proper unit tests and github workflow should be used rather than manual testing.
