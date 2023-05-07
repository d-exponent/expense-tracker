FROM python:3.10-windowsservercore-1809

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./

EXPOSE 8000 5432

CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]