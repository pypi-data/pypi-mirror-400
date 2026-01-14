from setuptools import setup

setup(
    name="dew_ws_tools",
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    description="Manage internal Python tools for DEW Water Science",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dew-waterscience/dew_ws_tools",
    packages=["dew_ws_tools"],
    install_requires=["loguru", "pydata_sphinx_theme"],
    python_requires=">=3.8",
    entry_points="""
        [console_scripts]
        publish_locally=dew_ws_tools.publish_locally:main
    """,
)
