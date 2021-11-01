FROM python:3.8
WORKDIR /zest.releaser/
ENV PYTHONPATH=/zest.releaser/
ENV USER=root
RUN pip install -U pip setuptools zc.buildout && \
    apt-get update && \
    apt-get -y install git
RUN git config --global user.name "Temp user" && \
    git config --global user.email "temp@example.com" && \
COPY . /zest.releaser/
RUN buildout
CMD bin/test -v
