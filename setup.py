import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shopify-scrape",
    version="0.0.5",
    author="Loren Jiang",
    author_email="loren.jiang@gmail.com",
    description="Python module to scrape Shopify store URLs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loren-jiang/shopify-scrape",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
