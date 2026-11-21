# Hugging Face Space (Docker SDK). Serves the CaneMitra API on port 7860.
FROM python:3.11-slim

# Spaces run the container as user 1000
RUN useradd -m -u 1000 user
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    ANONYMIZED_TELEMETRY=False
WORKDIR /home/user/app

# CPU-only PyTorch (the default Linux build pulls ~1.5 GB of CUDA libraries)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY --chown=user requirements.txt .
RUN sed '/^torch==/d' requirements.txt > requirements-space.txt \
    && pip install -r requirements-space.txt

COPY --chown=user . .
USER user

# Build the Chroma index (and download the embedding model) while the image is built,
# so the Space starts fast and /ask works right away.
RUN python -m app.vectorstore

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]