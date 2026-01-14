from setuptools import setup, find_packages

setup(
    name="coincap-hedera-agent-kit-plugin",
    version="0.8",
    license="MIT",
    author="Henry Tong",
    author_email="taksantong@gmail.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/henrytongv/coincap-hedera-plugin-py",
    keywords="hedera agent-kit coincap web3",
    install_requires=[
        "hedera-agent-kit",
        "requests",
    ],
)
