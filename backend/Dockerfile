FROM public.ecr.aws/docker/library/python:3.14.0-slim
ARG environment_name
ENV environment=$environment_name
RUN apt update && \
    apt install -y gcc default-libmysqlclient-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.lock
CMD gunicorn -e DJANGO_SETTINGS_MODULE=config.settings.${environment} -c config/gunicorn.conf.py --bind 0.0.0.0:8000 config.wsgi
