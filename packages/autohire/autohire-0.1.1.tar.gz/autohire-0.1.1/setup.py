from setuptools import setup, find_packages
import pathlib

# Read the contents of your README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="autohire",
    version="0.1.1",
    description="AI-powered resume tailoring and job application assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YourUsername/AutoHire_AI",
    author="AutoHire Team",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ai, resume, career, automation, llm",
    packages=find_packages(),
    install_requires=[
        "chainlit>=1.0.0",
        "openai>=1.0.0",
        "langchain>=0.1.0",
        "langchain-openai",
        "langchain-community",
        "pypdf",
        "python-dotenv",
        "fpdf2",
        "beautifulsoup4",
        "python-docx"
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'autohire=autohire.core:main',
        ],
    },
)
