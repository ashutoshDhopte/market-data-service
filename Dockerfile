FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --upgrade -r requirements.txt

# Copy the rest of the app code
COPY . .

# The command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]