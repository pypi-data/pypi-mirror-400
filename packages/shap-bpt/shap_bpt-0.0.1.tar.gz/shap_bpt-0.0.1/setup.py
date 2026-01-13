from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np
import sys

import platform
is_windows = (platform.system()=='Windows')
is_mingw = is_windows and ('--compiler=mingw32' in sys.argv)

extra_compile_args=['-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION', 
                    '-Wunreachable-code']

from setuptools import Extension
import numpy as np
import platform
import sys

def extra_args_for_compiler():
    # MSVC vs gcc/clang flags
    if platform.system() == "Windows" and "--compiler=mingw32" not in sys.argv:
        # MSVC
        return ["/O2"]   # keep it minimal; distutils already adds /O2 usually
    else:
        # gcc/clang (Linux/macOS/MinGW)
        return [
            "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION",
            "-Wunreachable-code",
        ]



if is_mingw:
    extra_compile_args.append('-DMS_WIN64')


# ext_modules = cythonize([
#     Extension("shap_bpt.bpt", ["shap_bpt/bpt.pyx"],
#               include_dirs=[np.get_include()],
#               extra_compile_args=extra_compile_args
#     ),
# ])
ext_modules = [
    Extension(
        "shap_bpt.bpt",
        ["shap_bpt/bpt.pyx"],  # or .c fallback
        include_dirs=[np.get_include()],
        extra_compile_args=extra_args_for_compiler(),
    )
]

setup(
    name='shap_bpt',
    version='1.0',
    packages=['shap_bpt'],
    ext_modules=ext_modules,
    install_requires=['Cython',
                      'numpy',
                      'matplotlib',
                      'tqdm',
                      'scikit-image'],
)