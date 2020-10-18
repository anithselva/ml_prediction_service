FROM python:3.8

WORKDIR /server

# COPY requirements.txt .
EXPOSE 5000

# copy the content of the local src directory to the working directory
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./server/requirements.txt

# Need to wait for RabbitMQ to be in a healthy state before running the consumer
# wait_for_it.sh will try to communicate with rabbitmq:5672 and only proceed with running
# the consumer if it suceeds.
CMD ["./utils/wait_for_it.sh" ,  "rabbitmq:5672", "--strict" , "--timeout=30" , "--" , "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "5000"]