FROM pypy:3-7

RUN pypy -m ensurepip --default-pip

#ENV PYTHONDONTWRITEBYTECODE 1
#ENV FLASK_APP "main.py"
#ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1

RUN mkdir /app
WORKDIR /app
ENV HOME /app

# install rust
ENV RUST_VERSION stable
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain ${RUST_VERSION}
ENV PATH $PATH:$HOME/.cargo/bin
RUN rustup install nightly ; rustup default nightly
ENV KK 5

COPY Pip* /app/
ADD . /app

RUN pip install --upgrade pip && \
    pip install virtualenv

#RUN virtualenv --python pypy3 luncho_pypyenv
RUN /app/bin/install-packages.sh

ENTRYPOINT /app/bin/start-gunicorn.sh
