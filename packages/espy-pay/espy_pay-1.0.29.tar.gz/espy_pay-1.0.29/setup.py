from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "ESSL Payments Aggregator"
LONG_DESCRIPTION = "Internal helper package for ESSL online payment"
setup(
    name="espy_pay",
    version="1.0.29",
    author="Femi Adigun",
    author_email="femi.adigun@myeverlasting.net",
    description="Payment services aggregator for ESSL",
    packages=find_packages(),
    install_requires=[
        "bcrypt>=4.2.1",
        "pytest>=8.3.4",
        "pydantic>=2.10.6",
        "sqlalchemy>=2.0.37",
        "PyYAML>=6.0.2",
        "httpx>=0.28.1",
        "python-dotenv>=1.0.1",
        "stripe>=11.5.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=[
        "payment, essl, aggregator, paystack, stripe, interswitch, square, flutterwave, payant"
    ],
    license="MIT",
)
