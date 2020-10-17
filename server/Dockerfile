FROM python:3.8

WORKDIR /server

# COPY requirements.txt .
EXPOSE 5000

# copy the content of the local src directory to the working directory
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# command to run on container start
# CMD [ "python", "./server.py" ]
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "5000" ]