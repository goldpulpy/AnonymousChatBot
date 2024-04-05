FROM python:3.11-alpine
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "main.py"]