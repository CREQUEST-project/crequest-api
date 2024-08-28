FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app/

# Copy requirements.txt
COPY ./requirements.txt /app/

# Install dependencies using pip
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

ENV PYTHONPATH=/app/app

COPY ./scripts/ /app/

COPY ./alembic.ini /app/

COPY ./prestart.sh /app/

COPY ./app /app/app

# Install debugpy
RUN pip install debugpy -t /opt
