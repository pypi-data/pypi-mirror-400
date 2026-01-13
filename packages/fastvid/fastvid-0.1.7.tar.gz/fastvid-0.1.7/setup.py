from setuptools import setup, find_packages

setup(
    name="fastvid",  # 包名
    version="0.1.7",  # 版本号
    author="mellon",  # 作者
    author_email="mellon.email@example.com",  # 作者邮箱
    description="A GUI tool for video processing (acceleration, GIF conversion, compression).",  # 简短描述
    long_description=open("README.md").read(),  # 长描述（通常从 README.md 读取）
    long_description_content_type="text/markdown",  # 长描述格式
    url="https://github.com/yourusername/fastvid",  # 项目主页
    packages=find_packages(),  # 自动查找包
    include_package_data=True,  # 包含非代码文件（如资源文件）
    install_requires=[
        "customtkinter",  # 依赖库
    ],
    entry_points={
        "console_scripts": [
            "fastvid=fastvid.main:main",  # 命令行入口
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python 版本要求
)
