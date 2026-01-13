from setuptools import setup, find_packages

setup(
    name="afterbuild",
    version="1.5.0",  # ورژن جدید برای انتشار نسخه مستقل
    packages=find_packages(),
    include_package_data=True,  # بسیار مهم: برای خواندن MANIFEST.in
    install_requires=[],  # چون PyInstaller را در bin گذاشتید، دیگر نیازی به پیش‌نیاز نیست
    author="Your Name",
    description="Professional Standalone Executable Builder",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
