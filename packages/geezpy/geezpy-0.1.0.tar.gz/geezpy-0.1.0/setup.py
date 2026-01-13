from setuptools import setup, find_packages

setup(
    name='geezpy',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'geezpy': ['keywords.json'],
    },
    entry_points={
        'console_scripts': [
            'geezpy=geezpy.__main__:main',
        ],
    },
    install_requires=[
        # List any dependencies here, e.g., 'some_package>=1.0.0'
    ],
    author='Yonathan Yitagesu', # Replace with actual author name
    author_email='yonathanyitagesuaklilu@gmail.com', # Replace with actual email
    description='A Python library to enable coding with Amharic keywords.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/geezpy', # Replace with actual repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Localization',
    ],
    python_requires='>=3.8',
)
