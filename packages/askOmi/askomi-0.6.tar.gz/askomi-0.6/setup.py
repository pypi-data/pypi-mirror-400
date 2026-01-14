from setuptools import setup, find_packages

setup(
    name='askOmi',
    version='0.6',
    packages=find_packages(),
    install_requires=[
        'google-generativeai',
    ],  # list any dependencies
    author='Why Should I reveal',
    description='Hi Cutie',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
