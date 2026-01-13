from setuptools import setup, Extension
from Cython.Build import cythonize


extensions = [
    Extension(
        name="Ncore.tl",
        sources=["src/Ncore/tl.pyx"],
        extra_compile_args=['-O3'],
        language="c",
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': '3',
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'nonecheck': False,
            'initializedcheck': False,
        }
    ),
)
