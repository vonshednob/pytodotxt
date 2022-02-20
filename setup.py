import setuptools
import pathlib

from pytodotxt import version


with open('README.md', encoding='utf-8') as fd:
    long_description = fd.read()

with open('LICENSE', encoding='utf-8') as fd:
    licensetext = fd.read()


def collect_doc_helpers(subdir):
    basepath = pathlib.Path('doc/build/html')
    if not basepath.exists() or not (basepath / subdir).exists():
        return []

    return list(str(basepath / subdir / fn.name)
                for fn in (basepath / subdir).iterdir()
                if fn.is_file())


def example_files():
    path = pathlib.Path('./examples')
    return list('examples/' + fn.name for fn in path.iterdir() if fn.suffix == '.py')


setuptools.setup(
    name='pytodotxt',
    version=version.__version__,
    description="Library to access todo.txt-like task lists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://vonshednob.cc/pytodotxt",
    author="R",
    author_email="contact+pytodotxt@vonshednob.cc",
    packages=['pytodotxt'],
    data_files=[('share/doc/pytodotxt/html', collect_doc_helpers('')),
                ('share/doc/pytodotxt/html/_static', collect_doc_helpers('_static')),
                ('share/doc/pytodotxt/html/_sources', collect_doc_helpers('_sources')),
                ('share/doc/pytodotxt/examples', example_files())],
    python_requires='>=3.0',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',])
