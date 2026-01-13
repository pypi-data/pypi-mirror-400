# Publishing to PyPI

To publish the OpenTrace Python SDK to the Python Package Index (PyPI), follow these steps:

## 1. Preparation
Ensure your `pyproject.toml` has the correct version and metadata.
If the name `opentrace` is taken on PyPI, consider changing it to `opentrace-py` or `opentrace-sdk`.

## 2. Install Build Tools
You will need `build` and `twine`:
```bash
pip install --upgrade build twine
```

## 3. Build the Package
Run this command from the `python-sdk` directory:
```bash
python -m build
```
This will create a `dist/` folder with `.tar.gz` and `.whl` files.

## 4. Upload to TestPyPI (Optional but recommended)
First, verify everything looks good by uploading to the test environment:
```bash
python -m twine upload --repository testpypi dist/*
```
*Note: You need a TestPyPI account.*

## 5. Upload to PyPI (Production)
Once verified, publish it to the real "pip store":
```bash
python -m twine upload dist/*
```
*Note: You will need a PyPI API Token for this.*

## Monorepo vs Separate Repo?
- **Monorepo (Current)**: Easier to maintain code consistency. Changes in the server API and SDK can be tracked in the same PR.
- **Separate Repo**: Better for the user community. Users can star, watch, and open issues specifically for the SDK without being overwhelmed by the server-side code.

**Recommendation**: Keep it here while in active development (Beta). Once it stabilizes and you have more public users, move it to `github.com/opentrace/opentrace-python`.
