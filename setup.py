from setuptools import setup, find_packages

setup(
    name="recipes",
    version="0.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["fastapi", "uvicorn", "sqlalchemy", "psycopg2-binary", "python-jose", "passlib", "python-multipart", "alembic", "fastapi_pagination", "ingredient-parser-nlp", "python-magic"]
)
