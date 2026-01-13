from setuptools import setup

setup(
    name="mediahub",                 # PyPI package name, lowercase
    version="0.1.0",                 # Required
    description="MediaHub multimedia application",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Savage",
    author_email="savage@example.com",
    url="https://github.com/yourusername/MediaHub",
    packages=[
        "mediahub",
        "mediahub.audio",
        "mediahub.backdoors",
        "mediahub.playlist",
        "mediahub.settings",
        "mediahub.video"
    ],
    package_dir={"mediahub": "src/mediahub"},  # Map package to src folder
    install_requires=[
        "pygame",
        "opencv-python",
    ],
    python_requires=">=3.10",
)

