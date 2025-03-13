from setuptools import setup, find_packages

setup(
    name="cliche-cli",
    version="0.2.0",
    packages=find_packages() + ['draw', 'draw.durdraw'],
    include_package_data=True,
    install_requires=[
        'click>=8.0.0',
        'openai>=1.0.0',
        'anthropic>=0.7.0',
        'google-generativeai>=0.3.0',
        'psutil>=5.9.0',
        'requests>=2.28.0',
        'python-dotenv>=1.0.0',
        'asyncio>=3.4.3',
        'py3nvml>=0.2.7',
        'setuptools>=58.0.4',
        'crawl4ai==0.4.248',
        'beautifulsoup4>=4.11.0',
        'html2text>=2024.2.26',
        'mdformat>=0.7.0',  
        'black>=23.0.0',
        'pytest>=7.0.0',
        'pytest-asyncio>=0.21.0',
        'duckduckgo-search>=2.8.6',
        'rich>=13.0.0',
        'art>=6.0',
        'pydantic>=2.0.0',
        'python-unsplash>=1.1.0',
        'Pillow>=10.0.0',
        'python-magic>=0.4.27',
        'aiofiles>=22.1.0',
        'praw>=7.8.1',
        'ollama>=0.4.7',
        # External system dependency (not listed here, install manually):
        # chafa - terminal image viewer (recommended version 1.12.0+)
        # Ubuntu/Debian: sudo add-apt-repository ppa:hpjansson/chafa && sudo apt update && sudo apt install chafa
        # macOS: brew install chafa
    ],
    entry_points={
        'console_scripts': [
            'cliche=cliche.core:cli',
        ],
    },
)
