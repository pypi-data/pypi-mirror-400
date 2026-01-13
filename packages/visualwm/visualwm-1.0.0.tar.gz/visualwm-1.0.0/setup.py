"""
泄密警示明水印SDK安装配置
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="visualwm",
    version="1.0.0",
    author="VisualWM Team",
    author_email="visualwm@example.com",
    description="泄密警示明水印SDK - 支持图片、视频、文本多模态水印嵌入与提取",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/visualwm",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
        "opencv-python>=4.5.0",
        "numpy>=1.20.0",
        "python-docx>=0.8.11",
        "PyPDF2>=3.0.0",
        "reportlab>=3.6.0",
        "openpyxl>=3.0.0",
        "lxml>=4.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "visualwm=visualwm.cli:main",
        ],
    },
)
