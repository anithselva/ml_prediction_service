FROM python:3.8

WORKDIR /server

# COPY requirements.txt .
EXPOSE 5000

# copy the content of the local src directory to the working directory
COPY . .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./server/requirements.txt

# command to run on container start
# CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "5000"]
CMD ["./server/wait_for_it.sh" ,  "database:3306", "--strict" , "--timeout=30" , "--" , "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "5000"]