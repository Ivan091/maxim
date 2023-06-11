from setuptools import setup, find_packages

setup(
    name='your-package-name',
    version='1.0.0',
    author='Your Name',
    author_email='your@email.com',
    description='Description of your package',
    long_description='Longer description of your package',
    url='https://github.com/your-username/your-package-repo',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        'psycopg2',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'your-script-name=your_package_name.module_name:main',
        ],
    },
)
