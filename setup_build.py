# Jarvis AI OS - Build Configuration for Windows .exe

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = ""
if readme_file.exists():
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='jarvis-ai-os',
    version='2.0.0',
    author='Rohit Ghogare',
    author_email='rohitghogare2010@gmail.com',
    description='Advanced AI Operating System Assistant for Windows',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rohitghogare2010/Jarvis',
    project_urls={
        'Bug Tracker': 'https://github.com/rohitghogare2010/Jarvis/issues',
        'Documentation': 'https://github.com/rohitghogare2010/Jarvis#readme',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Desktop Environment :: Human Machine Interface',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    packages=find_packages(exclude=['tests', 'docs']),
    python_requires='>=3.10',
    install_requires=[
        'numpy>=1.24.0',
        'pandas>=2.0.0',
        'torch>=2.0.0',
        'transformers>=4.30.0',
        'diffusers>=0.20.0',
        'opencv-python>=4.8.0',
        'Pillow>=10.0.0',
        'speechrecognition>=3.10.0',
        'pyttsx3>=2.90',
        'psutil>=5.9.0',
        'pywin32>=306',
        'requests>=2.31.0',
        'cryptography>=41.0.0',
        'pyqt5>=5.15.0',
    ],
    extras_require={
        'dev': [
            'black>=23.7.0',
            'flake8>=6.1.0',
            'pytest>=7.4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'jarvis=Jarvis:main',
        ],
        'gui_scripts': [
            'jarvis-gui=JarvisGUI:main',
        ],
    },
    package_data={
        'jarvis': ['assets/*', 'styles/*', 'icons/*'],
    },
    include_package_data=True,
    zip_safe=False,
)