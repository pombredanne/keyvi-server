from setuptools import setup, Extension, Command, find_packages
import distutils.command.build as _build
import distutils.command.sdist as _sdist
import glob
import os
import re

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_DEV = 0
IS_RELEASED = False

VERSION = "{}.{}.{}".format(VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)
if not IS_RELEASED:
    VERSION += '.dev{}'.format(VERSION_DEV)

PACKAGE_NAME = 'keyviserver'

def generate_protocols():
    protos_root = '../proto'
    output_dir = 'src/py/keyviserver/proto'

    protos = glob.glob(os.path.join(protos_root, '*'))
    max_modification_time = max([os.path.getmtime(fn) for fn in protos])
    if not os.path.exists(os.path.join(output_dir, '__init__.py')) or max_modification_time > os.path.getmtime(output_dir):
        try:
            from grpc_tools import protoc
        except ImportError:
            print("grpcio-tools not found.\n"
                  "Install it via pip (pip3 install grpcio-tools).")
            exit(1)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        protoc.main((
            '',
            '-I' + protos_root,
            '--python_out=' + output_dir,
            '--grpc_python_out=' + output_dir,
            ' '.join(protos),
        ))
        with open(os.path.join(output_dir, '__init__.py'), 'w') as fd:
            fd.write('# generated by setup.py')

        # Postprocess imports in generated code
        for root, _, files in os.walk(output_dir):
            for filename in files:
                if filename.endswith('.py'):
                    path = os.path.join(root, filename)
                    with open(path, 'r') as f:
                        code = f.read()

                    # fix imports
                    code = re.sub(r'^import index_pb2', r'import keyviserver.proto.index_pb2',
                                  code, flags=re.MULTILINE)

                    with open(path, 'w') as f:
                        f.write(code)

def write_version_file():
    here = os.path.abspath(os.path.dirname(__file__))
    version_file_path = os.path.join(here, 'src/py/keyviserver/_version.py')
    content = """
# THIS FILE IS GENERATED FROM KEYVISERVER SETUP.PY

__version__ = '{}'

""".format(VERSION)

    with open(version_file_path, 'w') as f_out:
        f_out.write(content)

install_requires = []

class build(_build.build):
    def run(self):
        generate_protocols()
        _build.build.run(self)


class sdist(_sdist.sdist):

    def run(self):
        generate_protocols()
        _sdist.sdist.run(self)

commands = {'sdist': sdist, 'build': build}

write_version_file()
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description='Python bindings for keyviserver',
    author='Hendrik Muhs',
    author_email='hendrik.muhs@gmail.com',
    license="ASL 2.0",
    cmdclass=commands,
    scripts=[],
    packages=find_packages(where = 'src/py'),
    package_dir={'': 'src/py'},
    zip_safe=False,
    url='http://keyvi.org',
    download_url='https://github.com/KeyviDev/keyviserver/tarball/v{}'.format(VERSION),
    keywords=['keyvi', 'key-value store'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires,
)
