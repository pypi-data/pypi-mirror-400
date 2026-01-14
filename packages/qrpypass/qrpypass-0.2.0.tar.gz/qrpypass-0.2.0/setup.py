from setuptools import setup, find_packages

setup(
    name="qrpypass",
    version="0.2.0",
    description="Headless QR decoder + TOTP authenticator Flask mini-service",
    author="Josh Gompert",
    author_email="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "opencv-python>=4.8.0",
        "cryptography>=41.0.0",
        "Flask>=3.0.0",
        "qrcode[pil]>=7.4.2",
        "Pillow>=10.0.0",
    ],
    python_requires=">=3.9",
)
