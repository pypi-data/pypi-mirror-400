from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clouditia-manager",
    version="1.2.0",
    author="Aina KIKI-SAGBE",
    author_email="support@clouditia.com",
    maintainer="Aina KIKI-SAGBE",
    maintainer_email="support@clouditia.com",
    description="Manage GPU sessions on Clouditia platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://clouditia.com",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="gpu cloud remote-execution machine-learning deep-learning pytorch tensorflow cuda jupyter api",
    project_urls={
        "Documentation": "https://clouditia.com/docs/manager-sdk",
        "Bug Reports": "https://github.com/clouditia/clouditia-manager/issues",
        "Source": "https://github.com/clouditia/clouditia-manager",
    },
)
