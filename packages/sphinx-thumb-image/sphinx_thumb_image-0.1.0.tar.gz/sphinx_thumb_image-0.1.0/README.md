# sphinx-thumb-image

Resize images in Sphinx documents/pages to thumbnails.

The purpose of this extension is to save on web storage costs and bandwidth fees, including data rates your visitors may
incur from image-heavy documentation. If the fullsize image is not referenced by another image directive it won't be copied
into your build's output directory.

* Python 3.9 through 3.14 supported on Linux, macOS, and Windows.

📖 Full documentation: https://sphinx-thumb-image.readthedocs.io

[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI][pypi-badge]][pypi-link]
[![PyPI Downloads][pypi-dl-badge]][pypi-dl-link]

[github-ci]: https://github.com/Robpol86/sphinx-thumb-image/actions/workflows/ci.yml/badge.svg?branch=main
[github-link]: https://github.com/Robpol86/sphinx-thumb-image/actions/workflows/ci.yml
[codecov-badge]: https://codecov.io/gh/Robpol86/sphinx-thumb-image/branch/main/graph/badge.svg
[codecov-link]: https://codecov.io/gh/Robpol86/sphinx-thumb-image
[rtd-badge]: https://readthedocs.org/projects/sphinx-thumb-image/badge/?version=latest
[rtd-link]: https://sphinx-thumb-image.readthedocs.io/en/latest/?badge=latest
[pypi-badge]: https://img.shields.io/pypi/v/sphinx-thumb-image.svg
[pypi-link]: https://pypi.org/project/sphinx-thumb-image
[pypi-dl-badge]: https://img.shields.io/pypi/dw/sphinx-thumb-image?label=pypi%20downloads
[pypi-dl-link]: https://pypistats.org/packages/sphinx-thumb-image

## Quickstart

To install run the following:

```bash
pip install sphinx-thumb-image
```

To use in Sphinx simply add to your `conf.py`:

```python
extensions = ["sphinx_thumb_image"]
```

And in your Sphinx documents:

```rst
.. thumb-image:: pictures/photo.jpg
    :resize-width: 100px
```
