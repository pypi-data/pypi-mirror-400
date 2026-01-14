```
pip install -r ./requirements.txt -i https://mirrors.tencent.com/pypi/simple
pip install wheel setuptools -i https://mirrors.tencent.com/pypi/simple
python -m pip install twine  -i https://mirrors.tencent.com/pypi/simple
python setup.py sdist bdist_wheel
python -m build
pip install .
pip install -e .
pip install -e .[dev]
python -m twine upload dist/*
```
```shell
pip install -e .
```
```shell
python setup.py sdist bdist_wheel
```
```shell
python -m twine upload dist/*
```
