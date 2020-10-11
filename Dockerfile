FROM python:3.7-alpine
WORKDIR /app
ENV FLASK_APP=fibonacci.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV FLASK_DEBUG=False
ENV REDIS_HOST=redis_server
COPY requirements.txt /app/requirements.txt
COPY fibonacci.py /app/fibonacci.py
RUN pip install -r requirements.txt
EXPOSE 5000/tcp
CMD ["flask", "run"]
