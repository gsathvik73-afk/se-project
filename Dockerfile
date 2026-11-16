FROM python:3.11-slim
WORKDIR /app
COPY requirements-lock.txt .
RUN pip install --no-cache-dir -r requirements-lock.txt && useradd --create-home appuser
COPY smartexpense smartexpense
COPY scripts/container-entrypoint.sh /entrypoint.sh
RUN mkdir -p /app/instance && chown -R appuser:appuser /app && chmod 755 /entrypoint.sh
USER appuser
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
