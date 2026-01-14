import setuptools

with open("README.md", "r") as file_header:
    long_description = file_header.read()

setuptools.setup(
    name='k2-connect',
    version='1.2.7',
    author='Philip Wafula, David Mwangi',
    author_email='philipwafula2@gmail.com, david.mwangi@kopokopo.com',
    description='A python SDK to connect to Kopo Kopo API',
    long_description=long_description,
    python_requires='>=3',
    install_requires=open("requirements.txt").readlines(),
    long_description_content_type='text/markdown',
    url='https://github.com/kopokopo/k2-connect-python',
    license='MIT',
    packages=setuptools.find_packages(exclude=['docs', 'tests*', 'example']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
