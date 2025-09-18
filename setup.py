from setuptools import setup, find_packages

setup(
    name='coderevitalize',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'coderevitalize = coderevitalize.cli:main',
        ],
    },
    install_requires=[
        'radon==6.0.1',
    ],
    author='Jules',
    author_email='jules@example.com',
    description='A tool to analyze Python code for "aged" or inefficient patterns.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/example/coderevitalize', # Placeholder URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Placeholder License
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
