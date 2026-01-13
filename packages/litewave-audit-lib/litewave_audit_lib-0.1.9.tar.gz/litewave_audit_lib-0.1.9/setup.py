from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements file
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh.readlines() if line.strip() and not line.startswith("#")]

setup(
    name="litewave-audit-lib",
    version="0.1.9",
    author="Sonu Sudhakaran",
    author_email="sonu@litewave.ai",
    description="A lightweight audit logging library with pluggable backends",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aiorch/litewave-audit-lib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",  # Update based on your actual license
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="audit logging nats microservices",
    project_urls={
        "Bug Reports": "https://github.com/aiorch/litewave-audit-lib/issues",
        "Source": "https://github.com/aiorch/litewave-audit-lib",
        "Documentation": "https://github.com/aiorch/litewave-audit-lib#readme",
    },
    include_package_data=True,
    zip_safe=False,
) 