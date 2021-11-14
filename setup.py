import setuptools

from pytodotxt import version


with open('README.md', encoding='utf-8') as fd:
    long_description = fd.read()

with open('LICENSE', encoding='utf-8') as fd:
    licensetext = fd.read()


setuptools.setup(
    name='pytodotxt',
    version=version.__version__,
    description="Library to access todo.txt like task lists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vonshednob/pytodotxt",
    author="R",
    author_email="devel+pytodotxt@kakaomilchkuh.de",
    packages=['pytodotxt'],
    data_files=[],
    python_requires='>=3.0',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',])

