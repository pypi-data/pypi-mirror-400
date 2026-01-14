from setuptools import setup

setup(
    name='pyruster',
    version='0.1.12',
    author='Elling',
    description='Implementing some syntax like rust.',
    long_description=open('README.rst').read(),
    license='MIT',
    install_requires=[
    ],
    packages=["pyruster", ],
    package_dir={"": "src"},
    package_data={"pyruster": ["py.typed", "*.pyi"]},
    python_requires=">=3.6",
)
