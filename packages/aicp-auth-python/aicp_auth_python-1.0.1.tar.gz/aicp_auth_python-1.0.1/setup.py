from setuptools import setup, find_packages

setup(
    name="aicp-auth-python",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "PyJWT>=2.0.0",
        "cryptography>=3.0.0",
        "python-keycloak>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "pre-commit>=2.15.0",
        ],
        "flask": ["flask>=2.0.0"],
        "fastapi": ["fastapi>=0.68.0", "uvicorn>=0.15.0"],
    },
    python_requires=">=3.8",
)

