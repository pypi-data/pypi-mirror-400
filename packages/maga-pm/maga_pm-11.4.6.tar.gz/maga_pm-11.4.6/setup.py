from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="maga-pm",
    version="11.4.6",
    description="MAGA Package Manager - Advanced package management with policy-based controls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ruin321",
    author_email="3791944372@qq.com",
    url="https://gitee.com/ruin321/maga-pm",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "maga=maga_pm.cli:main",
            "maga-pm=maga_pm.cli:main",
        ],
    },
    install_requires=[
        "requests>=2.25.0",
        "colorama>=0.4.0",
        "tqdm>=4.65.0",
        "nodejs>=0.1.1",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    keywords="maga, package manager, policy, control, management",
)
