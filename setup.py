from setuptools import setup,find_packages

VERSION = '0.0.1'
DESCRIPTION=''
LONG_DESCRIPTION=''

# Setting up
setup(
        name="WingWatch", 
        version=VERSION,
        author="Erik Carlson",
        author_email="erikvcarlson@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
                        "pytest==8.2.1",
                        "pandas==2.1.1",
                        "numpy==1.26.0",
                        "scipy==1.13.1",
                        "shapely==1.8.2",
                        "navpy==1.0",
                        "trimesh==4.4.3",
                        "pycork-0.1.0"
                        ],        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Linux :: Windows",

        ]
)
