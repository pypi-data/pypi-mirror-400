from setuptools import setup, find_packages

setup(
    name="viraxi",               
    version="0.0.1",
    packages=find_packages(),
    description="Viraxi research toolkit.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="jassem-manita",
    author_email="jasemmanita00@email.com",
    python_requires=">=3.10",
)
