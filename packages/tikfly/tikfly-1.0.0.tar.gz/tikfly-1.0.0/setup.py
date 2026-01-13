from setuptools import setup, find_packages

with open('README.md', 'r') as file:
  long_description = file.read()

setup(
  name='tikfly',
  version='1.0.0',
  author='Tikfly',
  author_email='hello@tikfly.io',
  description='Unofficial TikTok API Wrapped in Python',
  url='https://github.com/tikfly/tikfly-api-py',
  project_urls={
    'Documentation': 'https://docs.tikfly.io',
    'Source': 'https://github.com/tikfly/tikfly-api-py',
  },
  keywords=['tiktok', 'api', 'unofficial', 'python', 'tikfly'],
  packages=find_packages(),
  license='MIT',
  install_requires=[
    'aiohttp>=3.13.3,<4.0.0',
    'certifi>=2025.11.12',
  ],
  long_description=long_description,
  long_description_content_type='text/markdown'
)
