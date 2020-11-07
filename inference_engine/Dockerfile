FROM python:3.8

WORKDIR /inference_engine

# COPY requirements.txt .
EXPOSE 5672

# copy the content of the local src directory to the working directory
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./inference_engine/requirements.txt

# Need to wait for RabbitMQ to be in a healthy state before running the consumer
# wait_for_it.sh will try to communicate with rabbitmq:5672 and only proceed with running
# the consumer if it suceeds.
# Need to run inference.py as a module s.t parent directory is set based on dir that module was invoked from
CMD ["./utils/wait_for_it.sh" ,  "rabbitmq:5672", "--strict" , "--timeout=30" , "--" , "python" , "-m", "inference_engine.inference"]
