from setuptools import setup, find_packages

with open("README.md", "w", encoding="utf-8") as f:
    f.write("""# pantum_printer
专为 Windows 本地奔图打印机设计的 Python 工具包，支持中文、英文、混合文本及各类文档打印。

## 功能
1.  纯中文文本打印
2.  纯英文文本打印
3.  中英符号混合文本打印
4.  本地文档打印（需传完整路径）

## 依赖
- pywin32

## 使用方法
见测试脚本
""")

setup(
    name="pantum_printer",  # 包名，pip install 用
    version="1.0.0",
    author="翟梓豪",
    author_email="18341782191@163.com",  # 替换成你的邮箱
    description="Pantum Printer Python Local SDK",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # 自动识别子包
    install_requires=[
        "pywin32>=227"  # 依赖 pywin32 库
    ],
    python_requires=">=3.6",  # Python 版本要求
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)