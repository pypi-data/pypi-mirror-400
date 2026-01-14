from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="speedbuild",
    version="0.2",
    description="Extracts, adapts, and deploys battle-tested features from existing codebases to new projects—complete with all dependencies, configurations, and framework integrations.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Required for README.md
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "esprima",
        "textual",
        "readchar",
        "chromadb",
        "langgraph",
        "langchain",
        "django",
        
        # "fastmcp",

        # "langchain-openai",
        # "langchain-google-vertexai",
        # "langchain-anthropic",
        # "langchain-google-genai"
    ],
    entry_points={
        'console_scripts': [
            'speedbuild=speedbuild.sb:start',
        ],
    },
)
