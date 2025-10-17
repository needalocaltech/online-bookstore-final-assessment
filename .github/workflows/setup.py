from setuptools import setup, find_packages

setup(
    name='online_bookstore',
    version='1.0.0',
    packages=find_packages(),
    # Include all necessary files for installation
    include_package_data=True,
    # This line ensures models.py and app.py are visible
    py_modules=['app', 'models'], 
)
