from setuptools import setup, find_packages

setup(
    name="CloverAI",
    version="0.1.0",
    description="AI Governance Framework",
    author="Sashank Bhamidi",
    author_email="hello@sashank.wiki",
    url="https://github.com/shankypedia/CloverAI",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "aif360>=0.5.0",
        "diffprivlib>=0.5.0",
        "cryptography>=3.4.0",
        "pyyaml>=5.4.0",
        "kubernetes>=23.6.0",
        "prometheus-client>=0.12.0",
        "rich>=10.12.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=2.12.0",
            "black>=22.3.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "cloverai=cloverai.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)