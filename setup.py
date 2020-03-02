from setuptools import setup, find_packages
import os

# References and tools:
# * Cookiecutter
# * https://packaging.python.org/
# * https://setuptools.readthedocs.io
# * https://www.youtube.com/watch?v=4fzAMdLKC5k&t=1228s

# Notes:
# * You can use a setup.cfg file, c.f. https://setuptools.readthedocs.io/en/latest/setuptools.html
# * http://setuptools.readthedocs.io/en/latest/setuptools.html#new-and-changed-setup-keywords
# * http://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
# * https://github.com/pypa/sampleproject/issues/30
# * Do not use the old `data_files` keyword, it is very hard to get right. Use MANIFEST.in + include_package_data.
#   * Using `package_data` should generally also be avoided in favor of MANIFEST.in.
# Remember to clear the build/ and *.egg-info/*.wheel-info directories if you get any unexpected build behavior.

# Build and publish to PyPI:
#   python setup.py sdist bdist_wheel
#   twine check dist/*
#   twine upload -r testpypi dist/*
#   twine upload -r pypi dist/*

PROJECT_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(PROJECT_ROOT_DIR, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except IOError:
    long_description = """
# git-status-checker

Check the status of all your git repositories with a single command. 

Suitable for running as a scheduled task/job, which is useful if you want to make 
sure you haven't forgotten to commit or push changes to your git-controlled files. 

See `README.md` for usage.

"""
setup(
    name='git-status-checker',
    description='Check git repositories for uncommitted or unpushed changes.',
    version='2020.03.02',  # also update __version__ in ./git_status_checker/__init__.py
    url='https://github.com/scholer/git-status-checker',  # project home page
    project_urls={  # Additional, arbitrary URLs
        "Bug Tracker": "https://github.com/scholer/git-status-checker/issues",
        # "Documentation": "https://docs.example.com/HelloWorld/",
        "Source Code": "https://github.com/scholer/git-status-checker",
    },
    download_url='https://github.com/scholer/git_status_checker/archive/master.zip',  # Update for each new version
    license='GNU General Public License v3 (GPLv3)',
    author='Rasmus Scholer Sorensen',
    author_email='rasmusscholer@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # setuptools.find_packages() is generally preferred over manual listing.
    packages=find_packages(exclude=['bin', 'docs', 'tests', 'examples']),
    # Use MANIFEST.in to specify which non-package files to include in the distribution
    # package_data={'git_status_checker': ['data/*.txt']}  # Data to include for each package.
    # include_package_data=True,  # ONLY for data under revision control? Or maybe also MANIFEST.in?
    entry_points={
        'console_scripts': [
            # console_scripts should all be lower-case, else you may get an error when uninstalling:
            'git-status-checker=git_status_checker.git_status_checker:main',
        ],
        # 'gui_scripts': []
    },
    install_requires=[
        'pyyaml',
    ],
    keywords=[
        "Git", "Version control", "Development tools",
    ],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Environment :: Console',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: End Users/Desktop',

        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX :: Linux',
    ],
)
