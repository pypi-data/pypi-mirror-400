from setuptools import setup

setup(
    name="quakegen",
    version="0.1.0",
    long_description="QuakeGen",
    long_description_content_type="text/markdown",
    packages=["quakegen"],
    install_requires=["numpy",  "h5py", "matplotlib", "pandas"],
)
