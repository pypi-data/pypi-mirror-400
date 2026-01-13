from Cython.Build import cythonize
from setuptools import Extension, setup

extension = Extension(
    name="pyqqmusicdes",
    sources=[
        "lib/QQMusicDES/des.c",
        "lib/qqmusicdes.c",
        "src/pyqqmusicdes.pyx",
    ],
    depends=[
        "lib/QQMusicDES/des.h",
        "lib/qqmusicdes.h",
        "src/pyqqmusicdes.pyx",
    ],
    include_dirs=[
        "lib/QQMusicDES",
        "lib",
    ],
)

setup(
    ext_modules=cythonize([extension]),
    packages=["pyqqmusicdes"],
    package_data={"pyqqmusicdes": ["*.pyi"]},
)
