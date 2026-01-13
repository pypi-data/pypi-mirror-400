from setuptools import find_packages, setup

setup(
    name="lapizlab",
    packages=find_packages(include=["lapizlab"]),
    version="0.1.0",
    description="LapizLaboratory",
    author="ailapiz",
    license="AILL",
    install_requires=["numpy", "pandas"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    test_suite="tests",
)