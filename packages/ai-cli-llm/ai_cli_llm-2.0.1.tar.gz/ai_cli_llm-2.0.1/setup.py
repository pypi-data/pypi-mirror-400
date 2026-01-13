from setuptools import setup, find_packages

setup(
    name="ai-cli-llm",  
    version="2.0.1",
    author="Your Name",
    description="AI-powered CLI assistant with Gemini LLM command generation and human confirmation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.3.0",
        "requests>=2.28.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-cli=ai_cli.main:main"
        ]
    },
    python_requires=">=3.10",
)
