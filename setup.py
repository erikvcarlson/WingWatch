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
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Linux :: Windows",

        ]
)