FROM python:3.11-slim
WORKDIR /devopsproject
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
