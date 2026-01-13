from setuptools import setup, find_packages

setup(
    name="dnp3protocol",  # The name of your package
    version="21.06.018",  # Version number
    packages=find_packages(),  # Automatically find the packages
    #install_requires=["ctypes"],  # List dependencies here if there are any
    author="FreyrSCADA",
    author_email="contact@freyrscada.com",
    description="Distributed Network Protocol 3 (DNP3) protocol Server and Client Implementation - Python Wrapper ",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://www.freyrscada.com/dnp3-python.php",  # Replace with your repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",  # For Windows wheels
        "Operating System :: POSIX :: Linux",       # For Linux wheels
    ],
	package_data={'dnp3protocol': ['*.dll', '*.so'],'': ['tests/*']},
	include_package_data=True,  # This ensures non-Python files are included

)