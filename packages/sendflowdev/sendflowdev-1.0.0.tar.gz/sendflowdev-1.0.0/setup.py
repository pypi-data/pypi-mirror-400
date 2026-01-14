import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sendflowdev",
    version="1.0.0",
    author="Sendflow Team",
    author_email="support@sendflow.dev",
    description="Official Sendflow SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sendflowdev/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/sendflowdev/python-sdk/issues",
        "Documentation": "https://sendflow.dev/docs",
        "Homepage": "https://sendflow.dev",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
    },
)