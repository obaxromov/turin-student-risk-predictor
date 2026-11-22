# Hugging Face Spaces (Docker SDK) runs this. Locally:  docker build -t srp . && docker run -p 7860:7860 srp
FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /home/user/app

COPY --chown=user requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY --chown=user . .

# Train the model while the image is built, so the first visit does not wait for it.
RUN python -c "from core import service; service.bundle()"

EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
