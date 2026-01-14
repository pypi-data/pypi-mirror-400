from setuptools import setup, find_packages
import sys
import os 

sys.path.insert(0, os.path.join(os.getcwd(),r'src/finmetry'))
 
from version import version 


with open('README.md') as readme_file:
    readme = readme_file.read()


requirements = [
    "numpy",
    "pandas",
    "py5paisa",
]

setup_requirements = []

test_requirements = []

setup(
    name='finmetry',
    version=version,
    packages=find_packages(where="src"),  # Required
    url="https://github.com/dev-ddr/finmetry",
    description="Stock market data analysis", # Optional
    keywords='stock market, market, finanace, investment', # Optional

    python_requires=">=3.6, <4",
    author="Darshan Rathod, Sachin K S", # Optional
    author_email='darshan.rathod1994@gmail.com, sachinks@gmail.com', # Optional
    classifiers=[ # Optional
        'Development Status :: 2 - Pre-Alpha',
        
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        
        'Natural Language :: English',
        
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 3.6'
    ],
    package_dir={"": "src"},  # Optional
    install_requires=requirements, # Optional 
    long_description=readme, # Optional
    long_description_content_type="text/markdown", # Optional 

    # setup_requires=setup_requirements,
    # test_suite='tests',
    # tests_require=test_requirements,
    # zip_safe=False,
    # include_package_data=True,
)


