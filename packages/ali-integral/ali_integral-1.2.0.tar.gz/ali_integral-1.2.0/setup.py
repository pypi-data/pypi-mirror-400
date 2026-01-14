from setuptools import setup, find_packages

# Читаем README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ali_integral',
    version="1.2.0",
    description='A Python library for calculating Information Flux at the Cauchy Horizon',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Ali (Troxter222)',
    url='https://github.com/Troxter222/Ali_Integral_Project',
    packages=find_packages(include=['ali_integral', 'ali_integral.*']),
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'imageio'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)