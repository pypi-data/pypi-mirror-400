from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lcfv",
    version="0.1.0",
    author="Quan Wang",
    author_email="wangq10@rpi.edu",
    description="Label Consistent Fisher Vectors (LCFV)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wq2012/LCFV",
    package_dir={'': 'python'},
    packages=find_packages(where='python'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "scipy",
    ],
)
