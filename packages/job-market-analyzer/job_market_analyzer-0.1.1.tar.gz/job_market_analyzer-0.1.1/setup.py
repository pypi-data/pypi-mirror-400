from setuptools import setup, find_packages

setup(
    name="job-market-analyzer",
    version="0.1.1",
    author="Rahul",
    author_email="rahulgandhi1907@gmail.com",
    description="A Python package to analyze job market data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "matplotlib",
        "seaborn"
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
