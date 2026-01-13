from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
from pathlib import Path
import shutil

# This package lives in a monorepo. The canonical generator logic and vocabulary live under
# ../src, but sdists/wheels must be self-contained and cannot rely on files outside the
# python/ directory once published.

this_directory = Path(__file__).parent

# PyPI project description:
# - When building from an sdist, setuptools expects a README.md in the sdist root (python/).
# - When building locally from the monorepo, we use the repo root README.md.
readme_path = this_directory / "README.md"
if not readme_path.exists():
    readme_path = this_directory / ".." / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = ""


def _copy_vocabulary():
    # Keep src/vocabulary.txt as the single source of truth.
    # During local installs/builds from the monorepo, we copy it into the Python package
    # directory so the runtime loader can always read a packaged file.
    src_vocabulary = this_directory / ".." / "src" / "vocabulary.txt"
    dst_vocabulary = this_directory / "alex_jonesum" / "vocabulary.txt"
    if src_vocabulary.exists():
        # Always overwrite so installs pick up the latest src/vocabulary.txt
        dst_vocabulary.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_vocabulary, dst_vocabulary)


def _copy_c_core():
    # The Python extension compiles against a C source file that must be present inside
    # the Python sdist/wheel. When building from the monorepo we copy the C core into
    # python/alex_jonesum/ so that:
    # - `python -m build` (sdist -> wheel) works in isolated build envs
    # - the extension sources are self-contained for PyPI releases
    src_root = this_directory / ".." / "src"
    dst_root = this_directory / "alex_jonesum"
    dst_root.mkdir(parents=True, exist_ok=True)

    src_c = src_root / "jonesum.c"
    src_h = src_root / "jonesum.h"

    if src_c.exists():
        shutil.copy2(src_c, dst_root / "jonesum.c")
    if src_h.exists():
        shutil.copy2(src_h, dst_root / "jonesum.h")


# Native extension definition:
# - `_jonesum.c` is the CPython wrapper
# - `jonesum.c` is the C core implementation copied into the package by _copy_c_core()
jonesum_extension = Extension(
    "alex_jonesum._jonesum",
    sources=[
        "alex_jonesum/_jonesum.c",
        "alex_jonesum/jonesum.c",
    ],
    include_dirs=["alex_jonesum"],
    language="c",
)


class BuildExtWithData(build_ext):
    def run(self):
        # build_ext is the most reliable hook: it runs whenever we compile the extension
        # (including editable installs). Use it to refresh packaged data + C sources.
        _copy_vocabulary()
        _copy_c_core()
        super().run()


class BuildPyWithData(build_py):
    def run(self):
        # build_py runs when building pure-Python modules. We also refresh files here so
        # non-extension builds still have the latest vocabulary/C core copied in.
        _copy_vocabulary()
        _copy_c_core()
        super().run()


class SdistWithData(sdist):
    def make_release_tree(self, base_dir, files):
        # The sdist is the source artifact uploaded to PyPI. It must include:
        # - a top-level README.md for PyPI rendering
        # - the C core source/header under alex_jonesum/ so wheels can be built from sdist
        # - the vocabulary data under alex_jonesum/
        super().make_release_tree(base_dir, files)

        release_root = Path(base_dir)
        release_package_dir = release_root / "alex_jonesum"
        release_package_dir.mkdir(parents=True, exist_ok=True)

        # Ensure the sdist contains a top-level README.md with the same content as the
        # repo root README. PyPI will render this as the project description.
        repo_readme = this_directory / ".." / "README.md"
        if repo_readme.exists():
            shutil.copy2(repo_readme, release_root / "README.md")

        src_root = this_directory / ".." / "src"
        src_c = src_root / "jonesum.c"
        src_h = src_root / "jonesum.h"
        src_vocab = src_root / "vocabulary.txt"

        if src_c.exists():
            shutil.copy2(src_c, release_package_dir / "jonesum.c")
        if src_h.exists():
            shutil.copy2(src_h, release_package_dir / "jonesum.h")
        if src_vocab.exists():
            shutil.copy2(src_vocab, release_package_dir / "vocabulary.txt")

    def run(self):
        # When creating an sdist from the monorepo, make sure our working tree has the
        # generated package copies first (useful for local installs and consistency).
        _copy_vocabulary()
        _copy_c_core()
        super().run()


setup(
    name="alex-jonesum",
    version="2.0.0",
    description="Alex Jones Ipsum generator with C core and Python bindings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Emboiko",
    author_email="ed@emboiko.com",
    url="https://github.com/emboiko/alex_jonesum",
    packages=find_packages(),
    ext_modules=[jonesum_extension],
    cmdclass={
        "build_ext": BuildExtWithData,
        "build_py": BuildPyWithData,
        "sdist": SdistWithData,
    },
    package_data={
        "alex_jonesum": ["vocabulary.txt"],
    },
    include_package_data=True,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C",
    ],
)
