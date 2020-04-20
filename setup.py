from setuptools import setup, find_packages
setup(
    name                 = 'tak',
    version              = '0.2.0',
    install_requires     = [ 'jinja2~=2.10.1' ],
    package_dir          = { '': 'src' },
    packages             = find_packages('src'),
    include_package_data = True,
    package_data         = { 'tak': ['templates/*'] },
    data_files           = [('share/man/man1/', ['man/tak.1'])],
    python_requires      = '~=3.8',
    entry_points         = {
        'console_scripts': [
            'tak=tak:run',
        ],
    },

    author       = 'Balagopal Komarath',
    author_email = 'bkomarath@rbgo.in',
    description  = 'Create presentations that use the Takahashi method',
    license      = 'GPLv3',
    classifiers  = [
        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',

        'Topic :: Office/Business',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3.8',
    ],
    keywords     = 'tak takahashi presentation slideshow',
    url          = 'https://bkomarath.rbgo.in/tak',
    project_urls = {
        'Homepage'      : 'https://bkomarath.rbgo.in/tak',
        'Documentation' : 'https://bkomarath.rbgo.in/tak/man',
        'Source Code'   : 'https://www.github.com/balu/tak'
    }
)
