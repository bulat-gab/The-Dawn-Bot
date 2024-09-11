FROM python:3.12-alpine

WORKDIR app/

COPY requirements.txt .

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-warn-script-location --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "./run.py", "farm"]