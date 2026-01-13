from setuptools import setup, find_packages
import codecs
import os
from pathlib import Path

# here = os.path.abspath(os.path.dirname(__file__))

# with codecs.open(os.path.join(here, "Readme.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()

here = Path(__file__).parent.resolve()

# Read README if present (safe guard if missing)
readme_path = here / "Readme.md"
long_description = ""
if readme_path.exists():
    long_description = "\n" + readme_path.read_text(encoding="utf-8")


VERSION = "0.0.5"
DESCRIPTION = "Tool to simulate Spiking Neural Networks"


setup(
    name="nervos",
    version=VERSION,
    author="Jaskirat Singh Maskeen",
    author_email="<jsmaskeen@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "numpy",
        "pandas",
        "rich",
        "scikit-learn",
        "scipy"
    ],
    keywords=[
        "python",
        "spiking neural network",
        "simulation",
        "stdp",
        "snn",
        "neuromorphic computing",
        "mnist",
        "iris",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
