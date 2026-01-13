from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="grad-free-optim",
    version="0.0.3",
    author="Ricky Ding",
    author_email="e0134117@u.nus.edu",
    description="Gradient-free optimization of neural network parameters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NeuroAI-Research/grad-free-optim",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.8",
    license="MIT",
    keywords=[
        "machine-learning",
        "neural-networks",
        "gradient-free",
        "optimization",
        "genetic-algorithm",
        "pytorch",
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
