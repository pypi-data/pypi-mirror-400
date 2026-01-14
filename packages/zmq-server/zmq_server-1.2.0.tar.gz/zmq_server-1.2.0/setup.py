from setuptools import setup, find_packages
import os

# 读取 README.md 作为 long_description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="zmq-server",
    version="1.2.0",
    description="A ZeroMQ based message system with topic subscription, authentication, and heartbeat",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/zmq-server",  # 替换为你的GitHub地址
    author="haifeng",
    author_email="fenglex@126.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "zmq",
        "loguru"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking"
    ],
    python_requires=">=3.8",
    keywords="zmq message-system pubsub topic authentication heartbeat"
)
