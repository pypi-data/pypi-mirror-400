from setuptools import setup, find_packages

setup(
    name="driftimpact",
    version="1.1.0",
    description="A comprehensive library for data and concept drift detection with performance impact analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Serkan Arslan",
    author_email="arslanserkan0@gmail.com",
    url="https://github.com/serkanars/driftimpact",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
        "seaborn",
        "tabulate",
        "scikit-learn",
        "requests"
    ],
    python_requires=">=3.7",
)
