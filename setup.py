from setuptools import setup, find_packages

setup(
    name="cscs-tools",
    version="0.0.1",
    description="Utilities library",
    author="Csaba Cselko",
    author_email="lendoo73dev@gmail.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.8',
    install_requires=[]
)
