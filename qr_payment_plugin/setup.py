from setuptools import find_packages, setup

setup(
    name="qr_payment_plugin",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    description="Django plugin for QR payment, for use in multi-tenant project",
    author="Your Name",
    author_email="your.email@example.com",
    install_requires=[
        "django",
        "djangorestframework",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
    ],
)
