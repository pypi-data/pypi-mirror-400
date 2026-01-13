from setuptools import setup, find_packages

# read the contents of your README file
with open('README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

VERSION = '1.4.1'
DESCRIPTION = 'Visualization tool designed to analyze and illustrate the Lorenz Energy Cycle for atmospheric science.'

setup(
    name="lorenz_phase_space",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="Danilo Couto de Souza",
    author_email="danilo.oceano@gmail.com",
    license='MIT',
    packages=find_packages(),
    install_requires=['pandas', 'matplotlib', 'numpy', 'cmocean'],
    keywords=['lorenz', 'energy cycle', 'atmospheric science', 'cyclone', 'baroclinic', 'barotropic', 'visualization'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires='>=3.8',
)
