from setuptools import setup, find_packages

# 讀取README.md作為長描述
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "智能化的工作分配管理系統，能夠自動分析工作負載、優化人力配置，並生成詳細的分析報告。"

setup(
    name="work-assignment-manager",
    version="2.0.0",
    author="WorkFlow Optimization Team",
    author_email="support@assignment-manager.com",
    description="智能工作分配管理系統 - 自動化人力配置優化與分析報告生成",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-organization/work-assignment-manager",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "docs": [
            "sphinx>=3.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "assign-manager=main_manager:main",
            "workforce-analyzer=workforce_api:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Natural Language :: Chinese (Traditional)",
        "Natural Language :: English",
    ],
    keywords="工作分配 人力資源 任務調度 優化分析 workforce management task assignment",
    project_urls={
        "Bug Reports": "https://github.com/your-organization/work-assignment-manager/issues",
        "Documentation": "https://work-assignment-manager.readthedocs.io/",
        "Source": "https://github.com/your-organization/work-assignment-manager",
    },
    package_data={
        "": ["*.csv", "*.txt", "*.md"],
    },
    zip_safe=False,
) 