import sys
from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy as np


extensions = [
    Extension(
        name="itrigamma.citrigamma",
        sources=[
            "python/citrigamma.pyx",
            "src/itrigamma.c",
        ],
        include_dirs=[
            np.get_include(),
            "src",
        ],
        language="c",
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        extra_compile_args=["-O3"],
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
    ),
)
