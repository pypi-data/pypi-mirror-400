from setuptools import setup, find_packages

setup(
    name='neogram',
    version='9.3',
    description='neogram is a lightweight Python module for working with the Telegram Bot API and AI. It combines simple Telegram workflows with powerful features like text and image generation, translation, and more.',
    author='SiriLV',
    author_email='siriteamrs@gmail.com',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=['requests>=2.32.5', 'bs4>=0.0.2'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)