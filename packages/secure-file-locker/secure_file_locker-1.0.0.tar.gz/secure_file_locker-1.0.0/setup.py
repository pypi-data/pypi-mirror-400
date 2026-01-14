from setuptools import setup, find_packages

setup(
    name="secure-file-locker",
    version="1.0.0",
    author="Kaushik Basnet",
    author_email="kaushikbasnet@users.noreply.github.com",
    description="Offline secure file encryption application with modern UI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kaushikbasnet/Secure_File_Locker_App",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0",
        "customtkinter>=5.2.0"
    ],
    entry_points={
        "console_scripts": [
            "secure-file-locker=secure_file_locker.main:main"
        ]
    },
    python_requires=">=3.9",
)

