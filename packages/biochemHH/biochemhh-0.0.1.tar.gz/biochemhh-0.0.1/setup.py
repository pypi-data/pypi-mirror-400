from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="biochemHH",
    version="0.0.1",
    author="Otter Brown",
    author_email="",  # hidden for now
    description="Biochemistry & molecular biology helper tools",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        "biochemHH": ["example_input/*", "example_script/*"],
    },
    include_package_data=True,
    install_requires=[
    "biopython",
    "numpy",
    "scipy",
    "matplotlib",
    "pandas",
    "primer3-py",
    "pillow",
    "chardet",
    ],
    python_requires=">=3.8",
    license="GPL-2.0-only",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords="biochemistry molecular biology bioinformatics",
)
