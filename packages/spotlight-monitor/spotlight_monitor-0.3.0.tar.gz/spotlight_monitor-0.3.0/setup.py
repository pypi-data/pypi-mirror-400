from setuptools import setup, find_packages

setup(
    name="spotlight-monitor",
    version="0.3.0",
    description="AI-powered service monitoring SDK",
    author="Lore",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.24.0",
        "starlette>=0.27.0",
    ],
    extras_require={
        "fastapi": ["fastapi>=0.100.0"],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
