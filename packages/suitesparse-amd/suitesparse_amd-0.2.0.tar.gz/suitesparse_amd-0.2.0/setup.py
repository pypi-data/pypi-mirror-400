import os
import sys
from glob import glob

from setuptools import Extension
from setuptools import setup

amd_source_dir = os.path.join("SuiteSparse", "AMD", "Source")
amd_include_dir = os.path.join("SuiteSparse", "AMD", "Include")

amd_config_dir = os.path.join("SuiteSparse", "SuiteSparse_config")

amd_sources = glob(os.path.join(amd_source_dir, "*.c"))
amd_config_sources = glob(os.path.join(amd_config_dir, "*.c"))

define_macros = []

compilation_flags = []

if sys.platform == "win32":
    define_macros += [
        ("SUITESPARSE_HAVE_CLOCK_GETTIME", "0"),
        ("SUITESPARSE_CONFIG_HAS_OPENMP", "0"),
        ("SUITESPARSE_TIMER_ENABLED", "0"),
    ]
    compilation_flags += ['/O2', "-DNTIMER"]
else:
    compilation_flags += ['-O3']

setup(version="0.2.0",
      ext_modules=[Extension(name="suitesparse_amd._amd",
                             sources=['src/suitesparse_amd/_amd.c'] + amd_sources + amd_config_sources,
                             include_dirs=[amd_include_dir, amd_config_dir],
                             language="c",
                             define_macros=define_macros,
                             extra_compile_args=compilation_flags, )])
