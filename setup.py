from setuptools import setup

# flake8: noqa

VERSION = '0.0.4'
NAME = 'goodscloud_api_client'

tests_require = ['nose', 'coverage', 'responses']

setup(
    name = NAME,
    version = VERSION,
    description = "GoodsCloud API client",
    long_description = "",
    author = "GoodsCloud Inc.",
    author_email = 'dev@goodscloud.net',
    url = 'https://github.com/goodscloud/goodscloud',
    data_files = [("", ["LICENSE"])],
    license = 'BSD',
    classifiers=['License :: OSI Approved :: BSD License',],
    zip_safe = True,
    packages = [NAME,],
    package_data = {NAME: [],},
    entry_points = {
        'console_scripts': [
            'goodscloud_api_client=%s.client:main' % (NAME,),
            'test_%s=%s.test.run:run' % (NAME, NAME,),
        ],
    },
    install_requires = [
        'requests',
    ] + tests_require,
    test_suite = 'nose.collector',
    tests_require = tests_require,
)
