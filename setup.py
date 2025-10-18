from setuptools import setup, find_packages

setup(
    name='online_bookstore_app',
    version='1.0.0',
    description='Online Bookstore application source code.',
    author='Your Name',
    
    # This line tells Python to treat app.py and models.py as top-level modules
    # that can be imported using 'from app import ...' and 'from models import ...'.
    py_modules=['app', 'models'],
    
    # This ensures that any sub-directories containing __init__.py (like 'tests')
    # are recognized as packages, though we mainly rely on py_modules here.
    packages=find_packages(), 
    
    # We rely on requirements.txt for external dependencies, but you can list them here too.
    install_requires=[], 
)
