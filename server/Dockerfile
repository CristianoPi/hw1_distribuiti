FROM python:3.12.7

WORKDIR /app

COPY . .

RUN pip install mysql-connector-python grpcio grpcio-tools

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto

CMD ["python", "server.py"]