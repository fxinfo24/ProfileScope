from setuptools import setup, find_packages

setup(
    name="socialinsight",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "matplotlib>=3.4.0",
        "numpy>=1.20.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "pandas>=1.2.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for analyzing social media profiles",
    keywords="social media, analysis, profile, AI",
    url="https://github.com/yourusername/socialinsight",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
