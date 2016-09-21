from distutils.core import setup


with open('README.md') as readme:
    long_description = readme.read()


setup(
    name='django-transkribus',
    version='0.1.0',
    description='',
    url='http://github.com/django-transkribus',
    license='GNU General Public LIcense',
    install_requires=[
        'requests>=2.10.0',
        'eulxml>=1.1.3',
    ],
    description='Make RPC calls to Transkribus API from Django'
    long_description=long_description,
    packages=['transkribus'],
    platforms='any',
    classifiers = [
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Framework :: Django :: 1.10',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GPL-3.0',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing :: XML',
        ],
)
