
from setuptools import setup, find_packages

with open('backtrack_sampler/README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="backtrack_sampler",
    version="3.2.1",
    packages=find_packages(),
    description="An easy-to-understand framework for LLM samplers that rewind and revise generated tokens",
    author="Mihai Chirculescu",
    author_email="apropodemine@gmail.com",
    url="https://github.com/Mihaiii/backtrack_sampler",
    long_description=long_description,
    long_description_content_type='text/markdown',
)