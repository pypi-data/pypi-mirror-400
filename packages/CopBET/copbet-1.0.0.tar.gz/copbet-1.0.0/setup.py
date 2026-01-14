from setuptools import setup

setup(
    name='CopBET',
    version='1.0.0',    
    description='A Python wrapper for the Copenhagen Brain Entropy Toolbox (CopBET), originally developed by Anders S. Olsen.',
    url='https://github.com/shuds13/pyexample',
    author='Viswanath Missula',
    author_email='vmissul1@jh.edu',
    license='GNU General Public License 3.0',
    packages=['CopBET'],
    install_requires=[
                      'numpy',
                      'matlab',
                      'matplotlib',
                      'nibabel',
                      'pandas',
                      'scipy'
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
