from setuptools import setup, find_packages

setup(
    name='qmlpandas',
    version='0.0.1',
    description='A simple parser for QGIS style files to pandas DataFrame',
    long_description=open('USAGE.md').read(),
    long_description_content_type='text/markdown',
    author='Bas Altena',
    author_email='b.altena@zuiderzeeland.nl',
    packages=find_packages(),
    install_requires=[
        "pandas"
    ],
    license='APACHE',
    python_requires='>=3.12',
)