from pathlib import Path
import importlib
import os
import shutil
import subprocess
import sys

from loguru import logger


WHEEL_DESTINATIONS = [
    Path(r"p:\projects_gw\state\groundwater_toolbox\python\wheels"),
]

DOCS_BASE = Path(r"p:\projects_gw\state\groundwater_toolbox\python\wheels\docs")

DOCS_DESTINATIONS = [
    lambda **kwargs: Path(
        r"p:\projects_gw\state\groundwater_toolbox\python\wheels\docs"
    )
    / f"{kwargs['package_name']}"
    / f"{kwargs['version']}"
]

DOCS_INDEX_PAGE = """
<html>
<head>
<title>{package_name} documentation</title>
<style>
{style}
</style>
<body>
<h1>{package_name} documentation</h1>

<ul>
{versions_html}
</ul>

<p>See <a href="../index.html">here</a> for an index to all DEW Water Science Python package documentation.</p>

</body>
</html>
"""

DOCS_BASE_TITLE = "DEW Water Science Python package documentation"

DOCS_BASE_PAGE = """
<html><head><title>{DOCS_BASE_TITLE}</title>
<style>{style}</style></head>
<body><h1>{DOCS_BASE_TITLE}</h1>
<ul>{list_html}
</ul>
</body>
</html>
"""


STYLE = """
html {
    margin:    20px auto;
    max-width: 800px;
    min-width: 700px;
}

body {
    font-family: Segoe UI;
    font-size: 15px;
}

p, li, td {
    line-height: 1.3em;
}

a {
    color: rgb(0, 91, 129);
}

"""


def publish_locally(tag="latest_source", sphinx_build_options="", **kwargs):
    """Publish a built Python package internally at DEW Water Science.

    Args:
        tag (str): the tag which was just built by setuptool_scm e.g. 'v0.8'
            or 'latest_source', which means all you are doing is building docs.
            By default, 'latest_source' is used.
        sphinx_build_options (str): passed to sphinx-build on the command-line
            e.g. '-a'

    This should be run immediately after your normal steps for building a
    package e.g. after this kind of thing:

    .. code-block::

        $ git checkout main
        $ pytest
        $ git tag v0.8
        $ git push origin main --tags
        $ python -m build

    Steps this function does:

    1. Copies wheel file to package repositories: the Groundwater Toolbox folder,
       and the pypiserver on envtelem04. This step will be skipped if tag is
       'latest_source', because by definition that doesn't have a wheel file.
    2. Builds the Sphinx docs in the repository - this means you most definitely
       need the tag checked out, as per the code above.
    3. Copies the built Sphinx docs to the documentation location, which is
       also under the Groundwater Toolbox
    4. re-creates the "base" Sphinx docs page, to link between all the different
       packages and versions.

    Requires Python >= 3.8 for the update shutil.copytree function.

    """
    if sphinx_build_options == "-a":
        sphinx_build_options = "-a"
    else:
        sphinx_build_options = ""

    location = Path(os.getcwd()).absolute()
    package_name = location.stem.replace("-", "_")
    print(f"attempting to distribute package {package_name} {tag}")
    # print(f"testing import of {package_name}")
    # module = importlib.import_module(package_name)

    # print(f"test import of {package_name} was successful")
    # version = getattr(module, "__version__")
    # print(f"current version: {version}")

    assert tag == "latest_source" or tag.startswith("v")

    # Step 1 - copy wheel file to relevant destinations
    if tag != "latest_source":
        dist_folder = location / "dist"
        print(f"distribution folder: {dist_folder}")
        wheel_files = dist_folder.glob("*.whl")
        for wheel_file in wheel_files:
            wheel_package, wheel_version, *others = wheel_file.name.split("-")
            if f"v{wheel_version}" == tag or wheel_version == tag:
                print(f"located wheel for {tag}: {wheel_file}")

        for destination in WHEEL_DESTINATIONS:
            dest_file = destination / wheel_file.name
            shutil.copyfile(str(wheel_file), dest_file)
            print(f"copied {wheel_file} to {dest_file}")

    # Step 2 - build Sphinx docs
    with open("temp.bat", "w") as f:
        f.write(
            f"""
        call conda activate {os.environ['CONDA_DEFAULT_ENV']}
        call sphinx-build docs docs\_build\html {sphinx_build_options}
        """
        )
    p = subprocess.run(r".\temp.bat", shell=True, capture_output=True)
    print(p.stdout.decode("ascii"))
    print(p.stderr.decode("ascii"))
    os.remove("temp.bat")

    docs_path = location / "docs" / "_build" / "html"

    # Step 3 - copy Sphinx docs to relevant destinations
    for destination_gen in DOCS_DESTINATIONS:
        dest = destination_gen(package_name=package_name, version=tag)
        print(f"copying documentation build from {docs_path} to {dest}")
        shutil.copytree(docs_path, dest, dirs_exist_ok=True, copy_function=shutil.copy)
        package_dest = dest.parent
        package_index_html = generate_package_docs_index_page(package_dest)
        with open(package_dest / "index.html", "w") as f:
            f.write(package_index_html)
        print(f"created index page for {package_dest}")

    # Step 4 - recreate base sphinx page
    base = str(DOCS_BASE_PAGE)
    ul_html = []
    for path in DOCS_BASE.glob("*"):
        if path.is_dir():
            ul_html.append(f"<li><a href='{path.name}/index.html'>{path.name}</a></li>")
    list_html = "\n".join(ul_html)
    with open(DOCS_BASE / "index.html", "w") as f:
        f.write(
            base.format(
                list_html=list_html, style=STYLE, DOCS_BASE_TITLE=DOCS_BASE_TITLE
            )
        )


def generate_package_docs_index_page(path):
    package_name = path.name
    dirs = path.glob("*")
    ul_html = []
    versions = []
    for dirname in dirs:
        if dirname.is_dir() and (
            dirname.stem.startswith("v") or dirname.stem == "latest_source"
        ):
            version = dirname.name
            versions.append(version)
    final_versions = []
    if "latest_source" in versions[:]:
        final_versions.append("latest_source")

    final_versions += sorted(
        [v for v in versions if not v == "latest_source"],
        key=lambda version_string: [float(k) for k in version_string[1:].split(".")],
        reverse=True,
    )

    for version in final_versions:
        li = f"<li><a href='{version}/index.html'>{version}</a></li>"
        ul_html.append(li)
    html = str(DOCS_INDEX_PAGE).format(
        package_name=package_name,
        versions_html="\n".join(ul_html),
        style=STYLE,
    )
    return html


def main():
    return publish_locally(*sys.argv[1:])


if __name__ == "__main__":
    main()
