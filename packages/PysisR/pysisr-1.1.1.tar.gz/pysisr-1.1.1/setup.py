
from setuptools import setup, find_packages

setup(
    name="PysisR",
    version="1.1.1",
    packages=find_packages(),
    description="pip package minimum easy",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
)
