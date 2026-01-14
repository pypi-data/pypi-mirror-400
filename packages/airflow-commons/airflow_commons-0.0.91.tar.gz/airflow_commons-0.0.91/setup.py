import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airflow-commons",
    version="0.0.91",
    author="Startup Heroes",
    description="Common functions for airflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/migroscomtr/airflow-commons/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pytz>=2025.2",
        "datetime",
        "google-cloud-bigquery==3.40.0",
        "google-cloud-storage==3.7.0",
        "pandas",
        "sqlalchemy",
        "pymysql",
        "boto3==1.41.5",
        "botocore==1.41.5",
        "aiobotocore==2.26.0",
        "pyyaml",
        "s3fs==2025.12.0",
        "s3transfer",
        "pyarrow",
    ],
    include_package_data=True,
)
