from setuptools import setup, find_packages

setup(
    name="use-lightcurve",
    version="0.1.0",
    author="Lightcurve Team",
    author_email="founders@lightcurve.ai",
    description="Observability and evaluation SDK for LLM Agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/uselightcurve/lightcurve-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.10.0" 
    ],
)
