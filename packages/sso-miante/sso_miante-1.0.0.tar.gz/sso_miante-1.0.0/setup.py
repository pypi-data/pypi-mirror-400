from setuptools import setup, find_packages
import pathlib

BASE_DIR = pathlib.Path(__file__).parent

# README
readme_path = BASE_DIR / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="sso-miante",
    version="1.0.0",
    description="SSO Django Simplificado",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Jonathas Miante",
    license="MIT",

    python_requires=">=3.10",

    install_requires=["Django>=4.2", "requests>=2.32.5",],

    # Local dos packages (src/)
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    # IMPORTANTE: inclui templates/static/migrations no wheel
    include_package_data=True,

    package_data={
        "sso_miante": [
            "templates/**/*",
            "static/**/*",
            "migrations/**/*",
        ],
        "sso_miante_client": [
            "templates/**/*",
            "static/**/*",
            "migrations/**/*",
        ],
    },

    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)
