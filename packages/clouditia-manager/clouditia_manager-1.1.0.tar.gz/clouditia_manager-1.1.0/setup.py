from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clouditia-manager",
    version="1.1.0",
    author="Clouditia",
    author_email="support@clouditia.com",
    description="Manage GPU sessions on Clouditia platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://clouditia.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="gpu cloud computing ml machine-learning clouditia",
    project_urls={
        "Documentation": "https://clouditia.com/docs/manager-sdk",
        "Bug Reports": "https://github.com/clouditia/clouditia-manager/issues",
        "Source": "https://github.com/clouditia/clouditia-manager",
    },
)
