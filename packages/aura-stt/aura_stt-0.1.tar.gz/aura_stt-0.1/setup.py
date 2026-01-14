from setuptools import setup, find_packages
 
setup(
     name="aura_stt",
     version="0.1",
     author = "Dheer varsani",
     author_email="dheervarsani282@gmail.com",
     description="A package for speech to text conversion using web automation created by Dheer Varsani",
)
packages = find_packages(),
install_requires=[
    "selenium",
    "webdriver-manager"
]
