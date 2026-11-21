FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    HF_HOME=/hf_cache

# 1) CPU-only PyTorch. The default Linux torch downloads about 4 GB of CUDA libraries
#    that a CPU container never uses, and that download is what made the first build so slow.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch --index-url https://download.pytorch.org/whl/cpu

# 2) All other packages. The torch line is removed so pip keeps the CPU build from step 1.
#    The pip cache mount means a retry after a network error does not download everything again.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    sed '/^torch==/d' requirements.txt > requirements-docker.txt \
    && pip install -r requirements-docker.txt

# 3) The project (see .dockerignore for what is left out)
COPY . .

EXPOSE 8000 8501

# Default: the API. docker-compose.yml overrides this for the UI.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
