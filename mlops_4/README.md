# Image Classification with CI/CD (GitHub Actions)

A CNN-based image classifier for handwritten digits (MNIST), with an automated
GitHub Actions CI pipeline that runs the test suite on every push to `main`
or `master`.

## Project Structure

```
image-classification-project/
├── .github/
│   └── workflows/
│       └── ci.yaml          # CI pipeline definition
├── src/
│   ├── __init__.py
│   ├── model.py              # CNN architecture
│   ├── preprocess.py         # Data loading + preprocessing
│   ├── train.py               # Training script
│   └── predict.py            # Inference script
├── test.py                    # Test suite run by the CI pipeline
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Train the model (downloads MNIST automatically on first run):

```bash
python -m src.train --epochs 5
```

Run inference on a few test images:

```bash
python -m src.predict --model-path saved_model/mnist_cnn.keras
```

Run the test suite locally (same command the CI pipeline runs):

```bash
pytest test.py -v
```

## CI Pipeline

`.github/workflows/ci.yaml` defines a job that, on every push or pull
request targeting `main` or `master`:

1. Checks out the repository
2. Sets up Python 3.10
3. Installs dependencies from `requirements.txt` (with pip caching)
4. Runs `pytest test.py -v`

The tests use synthetic data (not a full MNIST download) so the pipeline
finishes in well under a minute and doesn't depend on flaky external
downloads.

## Getting the CI Screenshot for Submission

1. Push this project to a GitHub repository (see steps in chat).
2. Go to the repository's **Actions** tab on GitHub.
3. Open the latest workflow run — it should show a green checkmark.
4. Expand the **test** job and the **Run test suite** step to show the
   passing test output.
5. Screenshot the run summary (green check + workflow name) and, ideally,
   the expanded test log showing all tests passed.

## Submission Checklist

- [ ] Complete project source code
- [ ] `.github/workflows/ci.yaml`
- [ ] `test.py`
- [ ] Screenshot(s) of the passing GitHub Actions run
- [ ] All project/configuration files (`requirements.txt`, `.gitignore`, `README.md`)
