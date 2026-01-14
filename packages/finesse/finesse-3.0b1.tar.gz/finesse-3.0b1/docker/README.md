# Cython debug docker image for finesse

The setup for debugging Cython code is so tricky to setup correctly, that it is unlikely to get working in your development environment. Therefore we made this docker setup so you can do your debugging in this container. This also ensures that errors you see during debugging are not caused by your local environment, and will be reproducible by other people.

## Cython debugging documentation

The [official cython documentation](https://cython.readthedocs.io/en/latest/src/userguide/debugging.html) on debugging is not very clear and simply seems to be incorrect. There seems to be no need to run the debugger with python2 any more and the link to the example script is also outdated. I have not verified their comments on requiring a NumPy built with debug symbols. Their general instructions for running the debugger and the explanation of the commands seem to work. This docker image is based on an image by [Will Ayd](https://hub.docker.com/r/willayd/cython-debug#!) and the [blog post](https://willayd.com/fundamental-python-debugging-part-3-cython-extensions.html) that goes along with it. There is also a [merge request](https://github.com/cython/cython/pull/5186) open for Cython to fix the debug docs, which also contains some information. We decided to make our own image as to not rely on external sources. We also did some reporting in a [logbook post](https://logbooks.ifosim.org/finesse/2023/08/31/how-to-set-up-the-cython-debugger/), but this README will be the leading documentation since it lives right next to the docker setup.

## Exact setup and limitations

The general steps are the following:

1. Download and build the python source code with the debug flag enabled.
2. Download an compile `gdb`, linking it to the debug python.
3. Build finesse with the debug python and the cython debug flag.
4. Start up `cygdb` and run your python/cython example, still using the debug python

### Limitations/questions

- The cython documentation claims that gdb should be linked to a python2 installation. This does not seem to be necessary
- The documentation claims that the python compiled with debugging symbols is _only_ necessary for building and running your code, and the python linked against `gdb` can be a normal python. During compilation `gdb` rejected the following as 'not a suitable python': `python3` from the apt repository and `python-dbg` from the apt repository. It did accept the `python-dev` packages during compilation, but the debugging did not work.
- Cython debugging does not work with python 3.11 or python 3.12 out of the box, but by patching a specific functions in Cython's copy of `libpython.py`, it is functioning in python 3.11. Employing the same tactic for python 3.12 worked for most commands, but I did see an exception when running `cy globals`:

```bash
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/site-packages/Cython/Debugger/libpython.py", line 2045, in wrapper
    return function(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/Cython/Debugger/libcython.py", line 108, in wrapper
    function(self, *args, **kwargs)
  File "/usr/local/lib/python3.12/site-packages/Cython/Debugger/libcython.py", line 1212, in invoke
    v = v.get_truncated_repr(libpython.MAX_OUTPUT_LEN)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/Cython/Debugger/libpython.py", line 260, in get_truncated_repr
    self.write_repr(out, set())
  File "/usr/local/lib/python3.12/site-packages/Cython/Debugger/libpython.py", line 564, in write_repr
    pyop_attrdict = self.get_attr_dict()
                    ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/Cython/Debugger/libpython.py", line 522, in get_attr_dict
    assert dictoffset % _sizeof_void_p() == 0
AssertionError
```

- It should technically be possible to use a different python interpreter for `gdb` and for building and running your code. All the combinations I tried seemed not to work.
- None of the debugging works in cython 0.x, only ever got it working with cython3.

## How to build and use the container

The setup uses two containers, to avoid recompiling `gdb` and `python` whenever you reformat/change the docker file. The first file `gdb_python.Dockerfile` builds python 3.10 with the debug flag and compiles `gdb`, linking against the debug python. The second `Dockerfile`, installs cython3, clones the finesse repo (you can specify a commit reference with a build argument, the default is `develop`) and build finesse with the cython debug flag.

To build both images, use the `build_image.py` script:

```bash
usage: build-image.py [-h] [--no-cache] {3.10,3.11,3.12} [FINESSE_REF]

positional arguments:
  {3.10,3.11,3.12}  The python version to build the image with.
  FINESSE_REF       Optional argument specifying the finesse git reference. Defaults to 'develop'

options:
  -h, --help        show this help message and exit
  --no-cache        Disable using cache for building the docker image
```

Depending on your docker setup you might have to run this script with `sudo`.

Note that the script creates two tagged images:

- gdb-with-python:<python_version>
- finesse-cython-debug:<python_version>

Where the versioning of the images only depends on the python version, not the git reference. Building an image for the same python version with a different git reference will overwrite any existing image with the same python version. This should not be to much of a hassle, since it only has to recompile finesse.

Run docker image

```bash
docker run --rm -it finesse-cython-debug:<python_version>
```

Run test (inside the container) to ensure debugging works

```bash
docker/run-example
```

Should place a breakpoint in `finesse.simulations.base.ModelSettings.__init__` and show some context, eventually quitting the debugger

Note that the whole test can also be run by:

```bash
docker run --rm -it finesse-cython-debug:<python_version> /bin/bash docker/run-example
```

### Git and Docker

Using a git reference in a dockerfile does not always work the way you expect. Especially when you are using branch names, docker will not automatically 'know' that this branch had new commits pushed to it since the last time it built the docker file. Docker caches layers, and if you pass it a dockerfile with the exact same text as it has seen before, it will just revert to using the cache. The best way to guarantee that you are using the finesse version you need it to pass a commit hash as `FINESSE_REF`. Another workaround is using the `--no-cache` argument for `./build-image`, which will force it to build the image from scratch.

### Changing finesse version

To install a different version of finesse:

```bash
make realclean
git checkout <other_branch>
python -m pip install -e .
```

### Python version in the container

The image only contains a single python 3.10 interpreter, located in `/usr/local/bin/` (but symlinked to `python`). Using any kind of virtual environment will probably break the setup.
