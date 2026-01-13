from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ezicon",               # <--- The Install Name
    version="1.0.1",
    author="gusta01010",
    description="Create Windows Start Menu shortcuts for Python scripts instantly.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["ezicon"],            # Matches the filename 'pylnk.py'
    install_requires=["pywin32"],    # Auto-installs dependency
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        "console_scripts": [
            "ezicon=ezicon:main",      # <--- The Command (Type 'pylnk' to run)
        ],
    },
)