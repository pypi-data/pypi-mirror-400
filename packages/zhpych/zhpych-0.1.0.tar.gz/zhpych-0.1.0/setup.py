from setuptools import setup, find_packages

# 读取README.md作为长描述
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    # 注意：需修改为PyPI唯一名称（如cnpy-plus-zh，避免重复）
    name="zhpych",
    version="0.1.0",
    # 自动发现所有包
    packages=find_packages(),
    author="翟梓豪",
    author_email="18341782191@163.com",
    description="增强版中文Python语法解释器，全面支持中文变量名、函数名、类名",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 替换为你的GitHub仓库地址（可选）
    url="https://github.com/your-username/cnpy-plus",
    # 分类标签（便于PyPI搜索）
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Utilities"
    ],
    # Python版本要求
    python_requires=">=3.8",
    # 关键字（便于搜索）
    keywords=["chinese python", "cnpy plus", "中文编程", "中文变量名", "中文函数名"],
    # 无额外依赖，仅需Python标准库
    install_requires=[],
)