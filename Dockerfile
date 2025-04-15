FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt 


COPY main.py .
COPY tool/ tool/
COPY model/ model/
COPY agent/ agent/
 
# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8050"]
