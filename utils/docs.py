import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent.parent
geokdtree = root / "geokdtree" / "__init__.py"

VERSION = "1.3.0"
OLD_DOC_VERSIONS = ["1.2.4", "1.1.1", "1.0.1"]


def update_versions_manifest():
    """Write all available documentation versions to docs/versions.json and docs/versions.js."""
    versions = [VERSION] + OLD_DOC_VERSIONS
    versions_json = root / "docs" / "versions.json"
    versions_json.write_text(json.dumps(versions, indent=2) + "\n")

    versions_js = root / "docs" / "versions.js"
    versions_js.write_text(
        f"window.DOC_VERSIONS = {json.dumps(versions, indent=2)};\n"
    )


def generate_docs(version):
    out_dir = str(root / "docs" / version)
    template_dir = str(root / "doc_template")

    if version != "./" and version != VERSION:
        # One-time rebuild of older versions from dist/ tarballs
        tarball = str(root / "dist" / f"geokdtree-{version}.tar.gz")
        subprocess.run(
            [
                "uv",
                "run",
                "--isolated",
                "--with",
                tarball,
                "--with",
                "pdoc",
                "pdoc",
                "-o",
                out_dir,
                "-t",
                template_dir,
                "geokdtree",
            ],
            check=True,
            cwd=str(root),
        )
    else:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pdoc",
                "-o",
                out_dir,
                "-t",
                template_dir,
                "./geokdtree",
            ],
            check=True,
        )


# Build __init__.py from README
readme = (root / "README.md").read_text()
geokdtree.write_text(
    f'"""\n{readme}\n"""\n\ntry:\n    from geokdtree.cpp import GeoKDTree, KDTree\nexcept ImportError:\n    from geokdtree.geokdtree import GeoKDTree\n    from geokdtree.kdtree import KDTree\n'
)

# Update the versions manifest loaded dynamically by client-side JS
update_versions_manifest()

# Generate current docs
generate_docs("./")
generate_docs(VERSION)

# Rebuild old versions if '--rebuild-old' is passed or when executed with all
if "--rebuild-old" in sys.argv:
    for version in OLD_DOC_VERSIONS:
        print(f"Rebuilding docs for version {version}...")
        generate_docs(version)
