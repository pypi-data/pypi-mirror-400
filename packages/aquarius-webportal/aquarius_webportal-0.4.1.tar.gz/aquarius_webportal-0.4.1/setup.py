from setuptools import setup

setup(
    name="aquarius_webportal",
    packages=["aquarius_webportal"],
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    description="Python code to get data from implementations of Aquarius Web Portal",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kinverarity1/aquarius_webportal",
    author="Kent Inverarity",
    author_email="kinverarity@hotmail.com",
    license="MIT",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ),
    keywords="python groundwater data-access surface-water",
    install_requires=("requests", "pandas>=0.24.1", "lxml"),
    test_requires=(
        "pytest>=3.6",
        "pytest-cov",
        "coverage",
        "codecov",
        "pytest-benchmark",
        "black",
        "sphinx",
        "nbsphinx",
    ),
    include_package_data=True,
)
