ARG PYTHON_VERSION
FROM gdb-with-python:${PYTHON_VERSION}

# have to repeat the arg to have it availabe in this scope as weel
ARG PYTHON_VERSION
RUN apt-get update && apt-get upgrade -y

# finesse build-dependencies
RUN apt-get install -y libsuitesparse-dev

# for debugging make sure we run cython3 and enable the cython debug flag
RUN python -m pip install --upgrade cython>=3

ARG FINESSE_REF=develop

WORKDIR /home
RUN git clone https://gitlab.com/ifosim/finesse/finesse3.git
WORKDIR /home/finesse3
RUN git checkout ${FINESSE_REF}

ENV CYTHON_DEBUG=1
RUN python -m pip install -e .

# patch cython debugger so don't get lots of warning about open files
# and possibly work with python 3.11 and python 3.12
RUN patch /usr/local/lib/python${PYTHON_VERSION}/site-packages/Cython/Debugger/libpython.py < docker/PatchFile
# Try to prevent the debugger from paging
COPY .cygdbinit .cygdbinit
