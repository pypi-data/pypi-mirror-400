from setuptools import setup,find_packages

setup(
    name='jarvis-stt-god6217',
    version='0.1',
    author='Lajpal Mehdi',
    author_email='Lajpalmehdi08@gmail.com',
    description='this is speech to text package created by lajpal mehdi'
)
packages = find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]

