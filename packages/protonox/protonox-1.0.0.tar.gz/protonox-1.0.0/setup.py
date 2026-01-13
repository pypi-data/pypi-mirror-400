from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup


def read_requirements(filename: str) -> list[str]:
    requirements_path = Path(__file__).parent / filename
    requirements = []
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            requirements.append(cleaned)
    return requirements


setup(
    name="protonox",
    version="1.0.0",
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "protonox=protonox.__main__:main",
        ]
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Operating System :: OS Independent',
    ],
    description="Normalized Protonox Kivy toolchain, templates, and build utilities",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Juan David Morales - Protonox",
    author_email="protonox@example.com",
    url="https://github.com/ProtonoxDEV/Protonox-Kivy-Multiplatform-Framework",
    keywords=["kivy", "android", "buildozer", "python-for-android", "pyjnius", "cross-platform"],
)