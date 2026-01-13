from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

copt = {
    'msvc':    ['/Ox', '/std:c++20'],
    'mingw32': ['-O3', '-std=c++20'],
    'unix':    ['-O3', '-std=c++20'],
}

class build_ext_subclass(build_ext):
    def build_extensions(self):
        if (c := self.compiler.compiler_type) in copt:
            for e in self.extensions:
                e.extra_compile_args = copt[c]
        super().build_extensions()

setup(
    name="signum",
    version="1.2.0",
    ext_modules=[Extension("signum", ["signum.cpp"])],
    cmdclass={'build_ext': build_ext_subclass},
    include_package_data=True,
    install_requires=[],
    extras_require={
        'test': [
            'psutil',
            'sympy',
        ],
    },
)
