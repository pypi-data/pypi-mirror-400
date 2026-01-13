from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hookflow',
    version='1.0.0',
    author='Tekintian',
    author_email='tekintian@gmail.com',
    url='https://github.com/tekintian/hookflow',
    description='Git hooks manager. Fast, powerful, simple.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hookflow=hookflow.main:main'
        ],
    },
    package_data={
        'hookflow':[
            'bin/hookflow-linux-x86_64/hookflow',
            'bin/hookflow-linux-arm64/hookflow',
            'bin/hookflow-freebsd-x86_64/hookflow',
            'bin/hookflow-freebsd-arm64/hookflow',
            'bin/hookflow-openbsd-x86_64/hookflow',
            'bin/hookflow-openbsd-arm64/hookflow',
            'bin/hookflow-windows-x86_64/hookflow.exe',
            'bin/hookflow-windows-arm64/hookflow.exe',
            'bin/hookflow-darwin-x86_64/hookflow',
            'bin/hookflow-darwin-arm64/hookflow',
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Version Control :: Git'
    ],
    python_requires='>=3.6',
)
