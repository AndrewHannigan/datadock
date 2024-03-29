import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datadock",
    version="0.0.1",
    author="Andrew Hannigan",
    author_email="andrew.s.hannigan@gmail.com",
    description="Data blending utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrewhannigan/datadock",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "sqlparse",
        "click",
        "jinja2"
    ],
    entry_points = {
        'console_scripts': ['datadock=datadock.cli:datadock'],
    })