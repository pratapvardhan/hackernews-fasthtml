FROM python:3.10
WORKDIR /code
COPY --link --chown=1000 . .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1 PORT=7860
CMD ["python", "main.py"]