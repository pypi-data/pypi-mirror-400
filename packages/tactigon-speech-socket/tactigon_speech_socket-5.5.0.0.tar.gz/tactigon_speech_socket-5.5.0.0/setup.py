import codecs
import os.path
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
    Extension(name="tactigon_speech_socket.middleware.packet_manager", sources=["tactigon_speech_socket/middleware/packet_manager.c"]),
    Extension(name="tactigon_speech_socket.middleware.tactigon_speech", sources=["tactigon_speech_socket/middleware/tactigon_speech.c"]),
]

class build(build_orig):

    def finalize_options(self):
        super().finalize_options()
        __builtins__.__NUMPY_SETUP__ = False

        from Cython.Build import cythonize
        self.distribution.ext_modules = cythonize(self.distribution.ext_modules,language_level=3)

setup(
    name="tactigon_speech_socket",
    version=get_version("tactigon_speech_socket/__init__.py"),
    maintainer="Next Industries s.r.l.",
    maintainer_email="info@thetactigon.com",
    url="https://www.thetactigon.com",
    description="Tactigon Speech Socket perform stt over a audio stream sent by socket.",
    long_description=readme_file,
    long_description_content_type='text/markdown',
    keywords="tactigon,wereable,gestures controller,human interface,voice recognition,speech recognition,voice command,stt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8.0,<3.9.0",
    setup_requires=["cython"],
    install_requires=[
        "deepspeech_tflite==0.9.3",
    ],
    ext_modules=exts,
    include_package_data=True
)