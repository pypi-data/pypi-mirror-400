# setup.py
from setuptools import setup, find_packages
import os

def get_all_files(directory):
    """Recursively get all files relative to the package root."""
    paths = []
    for root, _, files in os.walk(directory):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, "transpdf")
            paths.append(rel_path)
    return paths

# Include all backend files (including node_modules/)
backend_files = get_all_files("transpdf/backend")

setup(
    name="transpdf",
    version="0.1.2",
    description="Translate PDFs to any language by also preserving layout and quality.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mukesh Anand G",
    author_email="ai.mukeshanandg@gmail.com",
    license="MIT",
    packages=find_packages(),
    package_data={"transpdf": backend_files},
    include_package_data=True,
    install_requires=["click>=8.0"],
    entry_points={
        "console_scripts": [
            "transpdf=transpdf.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: JavaScript",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
        "Topic :: Text Processing :: Linguistic",
    ],
)