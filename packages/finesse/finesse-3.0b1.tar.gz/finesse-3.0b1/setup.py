"""Setup file.

This file only contains the setup information for building Cython extensions. Everything
else is (and should be) in `pyproject.toml`. Eventually it should be possible to get rid
of `setup.py` and make the build system entirely declarative (see #367).
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from distutils.errors import CompileError
from pathlib import Path
from typing import KeysView, Optional, Sequence, Union
import warnings

from Cython.Build import build_ext, cythonize
from Cython.Distutils import Extension
from setuptools import setup

ROOT = Path(__file__).parent.absolute()
FINESSE_DIR = ROOT / "src" / "finesse"
SYS_NAME = platform.system()
NUM_JOBS = int(os.getenv("CPU_COUNT", os.cpu_count()))
CYTHON_DEBUG = bool(os.environ.get("CYTHON_DEBUG", False))

OPT_STR_LIST = Optional[Union[Sequence[str], str]]
OPT_PATH_LIST = Optional[Union[Sequence[Union[str, Path, None]], Union[str, Path]]]


class CompilationCheck:
    """Only reliable way to check if certain system libraries are available is to
    compile a small test program that tries to include them."""

    code: str = ""

    @classmethod
    def check(
        cls,
        include_paths: OPT_PATH_LIST = None,
        lib_paths: OPT_PATH_LIST = None,
        libs: OPT_STR_LIST = None,
        args: OPT_STR_LIST = None,
    ) -> bool:
        include_paths = cls._process_arg(include_paths)
        lib_paths = cls._process_arg(lib_paths)
        libs = cls._process_arg(libs)
        args = cls._process_arg(args)

        orig_dir = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                filename = r"test.c"
                with open(filename, "w") as file:
                    file.write(cls.code)
                with open(os.devnull, "w") as fnull:
                    args = [
                        os.environ.get("CC", "cc"),
                        filename,
                        *args,
                        *(f"-I{p}" for p in include_paths),
                        *(f"-L{p}" for p in lib_paths),
                        *libs,
                    ]
                    result = subprocess.call(args, stdout=fnull, stderr=sys.stderr)
            finally:
                os.chdir(orig_dir)

        return result == 0

    @staticmethod
    def _process_arg(arg: Union[OPT_PATH_LIST, OPT_STR_LIST]) -> list[str]:
        if arg is None:
            return []
        elif isinstance(arg, (str, Path)):
            return [str(arg)]
        elif isinstance(arg, (list, tuple)):
            return [str(a) for a in arg if a is not None]
        else:
            raise TypeError


class CheckOpenMP(CompilationCheck):
    code = r"""
        #include <omp.h>
        #include <stdio.h>
        int main() {
        #pragma omp parallel
        printf("Hello from thread %d, nthreads %d\n", omp_get_thread_num(), omp_get_num_threads());
        }
        """

    @classmethod
    def check(
        cls,
        include_paths: OPT_PATH_LIST = None,
        lib_paths: OPT_PATH_LIST = None,
        libs: OPT_STR_LIST = None,
        args: OPT_STR_LIST = None,
    ) -> bool:
        return super().check(include_paths, lib_paths, libs, args)


class CheckKLU(CompilationCheck):
    code = r"""
        #include "klu.h"
        int main() {
            klu_l_common klu;
            klu_l_defaults(&klu);
        }
        """

    @classmethod
    def check(
        cls,
        include_paths: OPT_PATH_LIST = None,
        lib_paths: OPT_PATH_LIST = None,
        libs: OPT_STR_LIST = None,
        args: OPT_STR_LIST = None,
    ) -> bool:
        return super().check(include_paths, lib_paths, libs, args)


def get_conda_paths() -> tuple[Path, Path] | tuple[None, None]:
    try:
        library = Path(sys.prefix)
        if sys.platform == "win32":
            library = library / "Library"
        return library / "include", library / "lib"
    except KeyError:
        return None, None


class finesse_build_ext(build_ext):
    def initialize_options(self):
        super().initialize_options()
        # default to parallel build
        self.parallel = NUM_JOBS


@dataclass
class ExtKwargs:
    """The optional arguments consisting of various directories, macros, compilation
    args, etc.

    that will be passed to Extension object constructor. See
    https://setuptools.pypa.io/en/latest/userguide/ext_modules.html#extension-api-
    reference
    """

    include_dirs: list[str] = field(default_factory=list)
    define_macros: list[tuple[str, str]] = field(default_factory=list)
    undef_macros: list[str] = field(default_factory=list)
    library_dirs: list[str] = field(default_factory=list)
    libraries: list[str] = field(default_factory=list)
    runtime_library_dirs: list[str] = field(default_factory=list)
    extra_objects: list[str] = field(default_factory=list)
    extra_compile_args: list[str] = field(default_factory=list)
    extra_link_args: list[str] = field(default_factory=list)
    export_symbols: list[str] = field(default_factory=list)
    cython_include_dirs: list[str] = field(default_factory=list)
    cython_directives: list[str] = field(default_factory=list)


def make_extension(relpath, **kwargs) -> Extension:
    import cython
    import numpy as np
    from packaging import version

    def construct_ext_name(rp):
        return ".".join(rp.with_suffix("").parts)

    ext_kwargs = ExtKwargs()
    ### Setting up some global options that need to be passed ###
    ###                   to all extensions                   ###

    # Include the src/finesse and NumPy header file directories
    ext_kwargs.include_dirs.extend([str(FINESSE_DIR), np.get_include()])
    # https://cython.readthedocs.io/en/latest/src/userguide/numpy_tutorial.html#compilation-using-setuptools
    if version.parse(cython.__version__).major >= 3:
        ext_kwargs.define_macros.append(
            ("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")
        )

    if SYS_NAME == "Windows":
        # switch off complex.h usage so we can use msvc's nonsensical complex
        # number implementation
        ext_kwargs.define_macros.append(("CYTHON_CCOMPLEX", "0"))

        # Try and get suitesparse from conda
        conda_include, conda_lib = get_conda_paths()

        if conda_include is not None:
            CONDA_SUITESPARSE_PATH = conda_include / "suitesparse"
            if CONDA_SUITESPARSE_PATH.exists():
                ext_kwargs.include_dirs.append(str(CONDA_SUITESPARSE_PATH))
            else:
                raise FileNotFoundError(
                    "Could not find suitesparse includes, install using `conda install suitesparse -c conda-forge`"
                )
            ext_kwargs.include_dirs.append(str(conda_include))
            ext_kwargs.library_dirs.append(str(conda_lib))
        else:
            # Can try and use a local build, this is something a user will have to
            # fight with themselves for now
            raise NotImplementedError(
                "User specificed Suitesparse installation required"
            )
    else:
        # Now ensure suitesparse headers get included
        USR_SUITESPARSE_PATH = Path("/usr/include/suitesparse")
        if USR_SUITESPARSE_PATH.exists():
            ext_kwargs.include_dirs.append(str(USR_SUITESPARSE_PATH))

        # Grab the paths to suitesparse from conda if using this
        conda_include, conda_lib = get_conda_paths()
        if conda_include is not None:
            CONDA_SUITESPARSE_PATH = conda_include / "suitesparse"
            if CONDA_SUITESPARSE_PATH.exists():
                ext_kwargs.include_dirs.append(str(CONDA_SUITESPARSE_PATH))

            ext_kwargs.include_dirs.append(str(conda_include))
            ext_kwargs.library_dirs.append(str(conda_lib))

    if SYS_NAME != "Windows":
        if CYTHON_DEBUG:
            ext_kwargs.extra_compile_args.extend(
                [
                    # As cython debugging (cygdb) only works with gdb improve
                    # debugging information for it. This might lead to problems
                    # when debugging on non-GNU platforms
                    "-ggdb",
                    # don't want optimization for debug builds
                    "-O0",
                ]
            )
        else:
            ext_kwargs.extra_compile_args.append("-O3")
    if sys.maxsize > 2**32 and sys.platform == "win32":  # 64-bit windows
        ext_kwargs.extra_compile_args.append("-DMS_WIN64")

    ### Now adding the optional extra args needed for this specific extension ###
    ext_kwargs_dict = asdict(ext_kwargs)
    for key, val in kwargs.items():
        if isinstance(val, str):
            val = [val]
        if key in ext_kwargs_dict:
            ext_arg = ext_kwargs_dict[key]
            assert isinstance(ext_arg, list)
            ext_arg.extend(val)

    sources = [str(FINESSE_DIR / relpath)] + kwargs.get("sources", [])
    return Extension(
        name=f"finesse.{construct_ext_name(relpath)}",
        sources=sources,
        language="c",
        **ext_kwargs_dict,
    )


def osx_openmp_check(open_mp_args, lib) -> bool:
    conda_include, conda_lib = get_conda_paths()
    open_mp_args["extra_link_args"] = [lib]
    # Using the above, check if openmp is actually available or not
    return CheckOpenMP.check(
        include_paths=conda_include,
        lib_paths=conda_lib,
        libs=open_mp_args["extra_link_args"],
        args=open_mp_args["extra_compile_args"],
    )


def scipy_cython_version_check() -> None:
    """Check that we don't use the unsupported combination of cython3 with SciPy<1.11.2.

    Note that we don't yet want to drop support for SciPy<1.11.2 because of the IGWN
    Conda environments.
    """
    import cython
    import scipy
    from packaging import version

    min_scipy_version = "1.11.2"

    if (
        version.parse(scipy.__version__) < version.parse(min_scipy_version)
        and version.parse(cython.__version__).major >= 3
    ):
        raise Exception(
            f"Installed cython>=3 requires SciPy version>={min_scipy_version}, but {scipy.__version__} is installed"
        )


def scipy_numpy_2_check() -> None:
    import scipy
    import numpy
    from packaging import version

    min_scipy_version = "1.13.0"

    if version.parse(numpy.__version__).major > 1 and version.parse(
        scipy.__version__
    ) < version.parse(min_scipy_version):
        raise Exception(
            f"Compiling with numpy2 requires SciPy version>={min_scipy_version}, "
            f"but {scipy.__version__} is installed"
        )


def numpy_1_check() -> None:
    import numpy
    from packaging import version

    if version.parse(numpy.__version__).major == 1:
        warnings.warn(
            "Compiling with numpy1 results in cython extensions incompatible "
            "with numpy2!"
        )


def get_ext_modules() -> Sequence[Extension]:
    conda_include, conda_lib = get_conda_paths()
    cmatrix_args = {"libraries": "klu"}
    compile_time_env = {"FINESSE3_DISABLE_OPENMP": 0}

    suitesparse_include = (conda_include, conda_include / "suitesparse")
    # Argument pattern for extensions requiring OpenMP are annoying
    # various openmp implementations exist. Generally ok on Linux and windows
    # but OSX clang doesn't support openmp out of the box...
    if SYS_NAME == "Darwin":
        FINESSE3_DISABLE_OPENMP = os.environ.get("FINESSE3_DISABLE_OPENMP", 0)

        if FINESSE3_DISABLE_OPENMP == "1":
            open_mp_args = {}  # empty so no openmp linked
            compile_time_env["FINESSE3_DISABLE_OPENMP"] = 1
        else:
            open_mp_args = {"extra_compile_args": ["-Xpreprocessor", "-fopenmp"]}
            # Try both the intel and llvm library, apparently exactly the same
            # apart from one small difference. The osx_openmp_check will update the
            # open_mp_args with the right library value to use
            if not osx_openmp_check(open_mp_args, "-liomp5"):
                if not osx_openmp_check(open_mp_args, "-lomp"):
                    # Empty the openmp compile arugments, this removes the build time
                    # linking to the libomp and allows for OSX to build and run perfectly
                    # fine without any. See issue #450 for some discussions
                    # open_mp_args = {}
                    compile_time_env["FINESSE3_DISABLE_OPENMP"] = 1
                    raise CompileError("OSX OpenMP libraries not found.")

        if not CheckKLU.check(
            include_paths=suitesparse_include,
            lib_paths=conda_lib,
            libs=["-lklu"],
        ):
            raise CompileError("KLU Suitesparse libraries not found.")
    elif SYS_NAME == "Windows":
        open_mp_args = {"extra_compile_args": "/openmp"}
        # No testing for dependencies on Windows for issue #271, msvc is too
        # much of a nusiance to quickly just try and compile from subprocesses
        # will need something like `from distutils.ccompiler import new_compiler`
        # https://github.com/astropy/astropy-helpers/blob/master/astropy_helpers/openmp_helpers.py
    else:
        open_mp_args = {
            "extra_compile_args": "-fopenmp",
            "extra_link_args": "-fopenmp",
        }

        if not CheckOpenMP.check(
            include_paths=conda_include,
            lib_paths=conda_lib,
            libs=open_mp_args["extra_link_args"],
            args=open_mp_args["extra_compile_args"],
        ):
            raise CompileError("No OpenMP libraries not found.")

        if not CheckKLU.check(
            include_paths=[*suitesparse_include, "/usr/include/suitesparse"],
            lib_paths=[str(conda_lib)],
            libs=["-lklu"],
        ):
            raise CompileError("KLU Suitesparse libraries not found.")

    # The argument patterns that get passed to all extensions
    default_ext_args = {}

    # See https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives
    # for in-depth details on the options for compiler directives
    compiler_directives = {
        # Embeds call signature in docstring of Python visible functions
        "embedsignature": True,
        # No checks are performed on division by zero (for big perfomance boost)
        "cdivision": True,
    }

    if os.environ.get("CYTHON_COVERAGE", False):
        # If we're in coverage report mode, then add the trace
        # macros to all extensions so that proper line tracing
        # is performed
        default_ext_args["define_macros"] = [
            ("CYTHON_TRACE", "1"),
            ("CYTHON_TRACE_NOGIL", "1"),
            ("CYTHON_USE_SYS_MONITORING", "0"),
            # see https://github.com/cython/cython/issues/6865#issuecomment-2872454304
        ]

        # Ensure line tracing is switched on for all extensions.
        compiler_directives["linetrace"] = True

    # If debug mode is set then ensure profiling
    # is switched on for all extensions
    if CYTHON_DEBUG:
        compiler_directives["profile"] = True

    # NOTE (sjr) Pass any extra arguments that a specific extension needs via a
    #            dict of the arg names: values here. See ext_args in make_extension
    #            function above for the options.
    ext_kwargs = {
        Path("enums.pyx"): default_ext_args,
        Path("cymath/*.pyx"): {**default_ext_args, **open_mp_args, **cmatrix_args},
        Path("thermal/*.pyx"): default_ext_args,
        Path("tree.pyx"): default_ext_args,
        Path("materials.pyx"): default_ext_args,
        Path("constants.pyx"): default_ext_args,
        Path("frequency.pyx"): default_ext_args,
        Path("parameter.pyx"): default_ext_args,
        Path("cyexpr.pyx"): default_ext_args,
        Path("element_workspace.pyx"): default_ext_args,
        Path("knm/*.pyx"): {**default_ext_args, **open_mp_args},
        Path("simulations/*.pyx"): default_ext_args,
        Path("simulations/sparse/*.pyx"): {**default_ext_args},
        Path("components/workspace.pyx"): default_ext_args,
        Path("components/mechanical.pyx"): default_ext_args,
        Path("components/modal/*.pyx"): default_ext_args,
        Path("detectors/workspace.pyx"): default_ext_args,
        Path("detectors/compute/amplitude.pyx"): default_ext_args,
        Path("detectors/compute/camera.pyx"): {**default_ext_args, **open_mp_args},
        Path("detectors/compute/power.pyx"): {**default_ext_args, **open_mp_args},
        Path("detectors/compute/quantum.pyx"): default_ext_args,
        Path("detectors/compute/gaussian.pyx"): default_ext_args,
        Path("tracing/*.pyx"): default_ext_args,
        Path("analysis/runners.pyx"): default_ext_args,
        Path("solutions/base.pyx"): default_ext_args,
        Path("solutions/array.pyx"): default_ext_args,
        Path("utilities/cyomp.pyx"): {**default_ext_args, **open_mp_args},
        Path("utilities/collections.pyx"): default_ext_args,
    }

    exts = []
    check_pyx_files(ext_kwargs.keys())
    for ext_rel_path, kwargs in ext_kwargs.items():
        exts.append(make_extension(ext_rel_path, **kwargs))

    return cythonize(
        exts,
        # Produces HTML files showing level of CPython interaction
        # per-line of each Cython extension (.pyx) file
        annotate=False,
        language_level=3,
        nthreads=NUM_JOBS,
        compiler_directives=compiler_directives,
        gdb_debug=CYTHON_DEBUG,
        compile_time_env=compile_time_env,
        build_dir="builddir",
        force=True if os.environ.get("CYTHON_FORCE", "0") == "1" else False,
    )


def check_pyx_files(pyx_files: KeysView[Path]) -> None:
    """Checks if the pyx files defined in the `ext_kwargs` dictionary match the files in
    the repo.

    Parameters
    ----------
    pyx_files : KeysView[Path]
        Dictionary keys of `ext_kwargs` dictionary

    Raises
    ------
    FileNotFoundError
        When a pyx file specified for an extension does not exist
    ValueError
        When the set of pyx files specified does not match the existing pyx files
    """
    all_pyx = []

    for p in pyx_files:
        p = FINESSE_DIR / p
        if p.exists():
            all_pyx.append(p)
        elif "*" in str(p):
            for res in p.parent.glob(str(p.parts[-1])):
                all_pyx.append(res)
        else:
            raise FileNotFoundError(f"pyx file {p} does not exist!")

    all_pyx_set = set(all_pyx)
    pyx_in_repo = set(
        path
        for path in FINESSE_DIR.rglob("*.pyx")
        if not any(part.startswith(".") for part in path.parts)
    )
    mismatch = all_pyx_set.symmetric_difference(pyx_in_repo)
    if mismatch:
        raise ValueError(
            f"Mismatch between pyx files defined for extensions and pyx files in repo: {mismatch}"
        )


if __name__ == "__main__":
    scipy_cython_version_check()
    scipy_numpy_2_check()
    numpy_1_check()
    setup(
        ext_modules=get_ext_modules(),
        cmdclass={"build_ext": finesse_build_ext},
        setup_requires=["setuptools_scm"],
    )
