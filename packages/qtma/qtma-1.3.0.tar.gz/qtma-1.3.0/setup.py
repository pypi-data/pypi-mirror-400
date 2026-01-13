from setuptools import setup, find_packages

setup(
    name='qtma',
    version='1.3.0',
    author='KonataLin',
    author_email='2424441676@qq.com',
    description='ADC Behavioral Event-Driven Simulator with Bukkit-style API',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/KonataLin/QuantiaMagica',
    packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
    license='MIT',
    keywords=['adc', 'analog-to-digital', 'simulation', 'sar', 'pipeline', 'sigma-delta', 'event-driven'],
    install_requires=[
        'numpy>=1.20.0',
        'matplotlib>=3.4.0',
    ],
    extras_require={
        'dev': ['pytest>=7.0.0', 'pytest-cov>=4.0.0', 'black>=22.0.0', 'flake8>=5.0.0'],
        'cuda': ['cupy>=11.0.0'],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
    ],
    include_package_data=True,
)