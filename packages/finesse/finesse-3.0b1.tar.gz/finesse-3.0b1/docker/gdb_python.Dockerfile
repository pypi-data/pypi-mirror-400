FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade -y

# prevent being asked for a timezone
ENV DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.10

# dependencies
RUN apt-get install -y \
    # to get python source and finesse source
    git \
    # for building python
    build-essential lcov pkg-config libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev lzma lzma-dev tk-dev uuid-dev zlib1g-dev \
    # for gdb
    libgmp-dev wget

# Clone and compile python with debug flag
RUN git clone -b ${PYTHON_VERSION} --depth 1 https://github.com/python/cpython.git /clones/cpython
RUN cd /clones/cpython && ./configure --with-pydebug CFLAGS="-g" && make -s -j$(nproc) && make install

# clone and compile gdb and link to python install
RUN cd /tmp && wget http://mirrors.kernel.org/sourceware/gdb/releases/gdb-13.2.tar.gz && tar -zxf gdb-13.2.tar.gz
RUN cd /tmp/gdb-13.2 && ./configure --with-python=python3
RUN cd /tmp/gdb-13.2 && make all install

# finesse makefile uses 'python' command for building
RUN ln -s /usr/local/bin/python${PYTHON_VERSION} /usr/local/bin/python
