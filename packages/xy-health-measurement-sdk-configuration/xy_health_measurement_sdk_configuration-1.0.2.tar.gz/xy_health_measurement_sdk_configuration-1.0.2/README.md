# 小阳心健康测量SDK Configuration Toolkit

## Conda
```bash
conda create -n measurement_sdk_configuration -y python=3.10 && \
conda activate measurement_sdk_configuration && \
pip install build toml twine && \
pip install -r <(python -c "import toml; print('\n'.join(toml.load('pyproject.toml')['project']['dependencies']))")
```

## publish
```bash
sudo rm -rf dist *.egg-info && \
python -m build

# publish to aliyun pypi
twine upload -r packages-pypi dist/*
# publish to pypi
python -m twine upload dist/*
```