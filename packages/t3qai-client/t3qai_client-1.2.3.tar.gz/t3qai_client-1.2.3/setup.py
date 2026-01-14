from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="t3qai_client",
    version="1.2.3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="t3qai client module",
    author="t3q",
    author_email="lab@t3q.com",
    url="",
    download_url="",
    install_requires=[
        "fastapi",
        "uvicorn",
        "pandas",
        "requests",
        "python-multipart",
        "filetype",
    ],
    packages=find_packages(exclude=[]),
    keywords=["t3q", "t3qai", "t3qai client", "t3qai_client"],
    python_requires=">=3",
    package_data={},
    zip_safe=False,
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
)
