from setuptools import setup, find_packages

# Baca README untuk long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="budiajimatrix",
    version="1.0.0",
    author="Ferdian Bangkit Wijaya",
    author_email="ferdian.bangkit@untirta.ac.id",  # Ganti dengan email Anda
    description="Library pengolahan matrix lengkap untuk Python - cocok untuk time series, GSTAR, VARIMA, dan analisis statistik",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ferdianwijayabangkit/budiajimatrix",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="matrix, linear algebra, statistics, time series, GSTAR, VARIMA, numpy, scipy",
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.18.0",
        "scipy>=1.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=20.8b1",
            "flake8>=3.8.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/ferdianwijayabangkit/budiajimatrix/issues",
        "Source": "https://github.com/ferdianwijayabangkit/budiajimatrix",
    },
)
