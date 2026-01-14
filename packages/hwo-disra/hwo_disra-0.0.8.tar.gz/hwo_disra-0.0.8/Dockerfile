FROM python:3.13

COPY requirements.txt .

RUN pip install -r requirements.txt && \
    pip install pytest pytest-cov uv ruff && \
    python -m ipykernel install --user --name python3

## DON'T FORGET --platform linux/amd64 DURING BUILD!!
