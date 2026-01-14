import codecs
import os.path
import sys
from pathlib import Path
from setuptools import setup, Extension, find_packages
from distutils.command.build import build as build_orig

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.lstrip().startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

here = Path(__file__).parent
readme_file = (here / "README.md").read_text()

exts = [
    Extension(name="tactigon_gear.middleware.adpcm_engine", sources=["tactigon_gear/middleware/adpcm_engine.c"]),
    Extension(name="tactigon_gear.middleware.packet_manager", sources=["tactigon_gear/middleware/packet_manager.c"]),
    Extension(name="tactigon_gear.middleware.tactigon_gesture", sources=["tactigon_gear/middleware/tactigon_gesture.c"]),
    Extension(name="tactigon_gear.middleware.tactigon_recorder", sources=["tactigon_gear/middleware/tactigon_recorder.c"]),
    Extension(name="tactigon_gear.middleware.utilities.data_preprocessor", sources=["tactigon_gear/middleware/utilities/data_preprocessor.c"]),
    Extension(name="tactigon_gear.middleware.utilities.tactigon_computing", sources=["tactigon_gear/middleware/utilities/tactigon_computing.c"]),
]

class build(build_orig):

    def finalize_options(self):
        super().finalize_options()
        __builtins__.__NUMPY_SETUP__ = False

        from Cython.Build import cythonize
        self.distribution.ext_modules = cythonize(self.distribution.ext_modules,language_level=3)

setup(
    name="tactigon_gear",
    version=get_version("tactigon_gear/__init__.py"),
    maintainer="Next Industries s.r.l.",
    maintainer_email="info@thetactigon.com",
    url="https://www.thetactigon.com",
    description="Tactigon Gear to connect to Tactigon Skin wereable platform",
    long_description=readme_file,
    long_description_content_type='text/markdown',
    keywords="tactigon,wereable,gestures controller,human interface",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.12.0",
    setup_requires=["cython"],
    install_requires=[
        "requests",
        "scipy",
        "bleak==2.0.0",
        "scikit-learn==1.6.0",
        "pandas==2.2.3",
    ],
    ext_modules=exts,
    include_package_data=True
)