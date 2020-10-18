FROM python:3.8

WORKDIR /inference_engine

# COPY requirements.txt .
EXPOSE 5672

# copy the content of the local src directory to the working directory
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./inference_engine/requirements.txt

# command to run on container start
CMD ["./inference_engine/wait_for_it.sh" ,  "rabbitmq:5672", "--strict" , "--timeout=30" , "--" , "python", "./inference_engine/inference.py"]

# CMD ["python", "./inference_engine/inference.py"]