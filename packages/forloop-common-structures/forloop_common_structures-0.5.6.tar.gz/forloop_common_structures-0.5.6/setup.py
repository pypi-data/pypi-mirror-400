import setuptools
    
with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name='forloop_common_structures',
    version='0.5.6',
    author='DovaX',
    author_email='dovax.ai@gmail.com',
    description='This package contains open source core structures and schemas within Forloop.ai execution core and API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/ForloopAI/forloop_common_structures',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          ''
     ],
    python_requires='>=3.6',
)
    