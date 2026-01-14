from setuptools import setup, find_packages

setup(
    name='CYPHER_STT',
    version='1.0.0',
    author='Ameer Omar',
    author_email='ameershaaban2004@gmail.com',
    description=' This is a Speech To Text package created by Ameer Omar'
)
packages=find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]
