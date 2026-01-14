from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='leitura_max_data_core',
    version='0.0.1',
    license='MIT License',
    author='Daniel Antunes Cordeiro',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='daniel.ant.cord@gmail.com',
    keywords='max-data-core',
    description=u'Pré processamento básico e leitura de dataframes',
    packages=['max-data-core'],
    install_requires=['requests', 'pandas' , 'polars'],)