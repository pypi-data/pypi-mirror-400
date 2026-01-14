from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='glauco-automacao-teste-25',
    version='1.0',
    description='Este pacote irá fornecer ferramentas de processamento de vídeo',
    long_description=Path('README.md').read_text(),
    author='Glauco',
    author_email='gvittibonturi@gmail.com',
    keywords=['camera', 'video', 'processamento'],
    packages=find_packages()
)
