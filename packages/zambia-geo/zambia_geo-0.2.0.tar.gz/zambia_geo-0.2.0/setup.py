from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setup(
    name="zambia-geo",
    version="0.2.0",
    author="Peter Sangwani Zyambo",
    author_email="zyambopeter1@gmail.com",
    description="A Python package containing Zambian provinces, cities, and constituencies data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sangwani-coder/zambia-geo",
    packages=find_packages(),
    include_package_data=True, # Important if you have JSON/CSV data files
    install_requires=[
        # Add any dependencies here, e.g., 'requests>=2.25.1'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="zambia, provinces, cities, constituencies, geography",
)