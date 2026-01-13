import setuptools
    
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name='flogg',
    version='1.0.1',
    author='DovaX',
    author_email='dovax.ai@gmail.com',
    description='Improved logging system for Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/DovaX/flog',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          
     ],
    python_requires='>=3.6',
)
    