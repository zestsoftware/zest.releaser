FROM python:3.8
WORKDIR /zest.releaser/
ENV PYTHONPATH=/zest.releaser/
ENV USER=root
RUN pip install -U pip setuptools tox && \
    apt-get update && \
    apt-get -y install git
COPY . /zest.releaser/
CMD tox -e py38
