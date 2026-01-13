from setuptools import setup, find_packages

setup(
    name="pyiec101",  # The name of your package
    version="21.6.18",  # Version number
    packages=find_packages(),  # Automatically find the packages
    #install_requires=["ctypes"],  # List dependencies here if there are any
    author="FreyrSCADA",
    author_email="contact@freyrscada.com",
    description="IEC 60870-5-101 protocol Server and Client Implementation - Python Wrapper for IEC 101 protocol",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://www.freyrscada.com/iec-60870-5-101-python.php",  # Replace with your repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",  # For Windows wheels
        "Operating System :: POSIX :: Linux",       # For Linux wheels
    ],
	package_data={'pyiec101': ['*.dll', '*.so'],'': ['tests/*']},
	include_package_data=True,  # This ensures non-Python files are included

)