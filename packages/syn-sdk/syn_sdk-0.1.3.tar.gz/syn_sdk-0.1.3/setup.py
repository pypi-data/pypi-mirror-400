from setuptools import setup, find_packages

setup(
    name="syn_sdk",
    version="0.1.3",
    description="syntac_realese_env",
    packages=find_packages(),
    author="lvsj",
    author_email="lvsj@sinxbot.com",
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "pillow==10.0.0",
        "numpy==1.26.4",
        "opencv-python==4.9.0.80",
        "scipy>=1.13.1",
        "torch>=2.1.2",
        "torchvision>=0.16.2",
        "matplotlib>=3.9.1",
        "ffmpeg-python",
        "pyudev==0.24.4",
        "lightning>=2.0.9.post0",
        "xformers>=0.0.21",
        "scikit-learn>=1.6.1",
        "triton>=2.1.0",
        "pyserial",
        "omegaconf",
        "einops",
        "pyarmor==8.*"
    ],
    # python_requires=">=3.9.2",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
