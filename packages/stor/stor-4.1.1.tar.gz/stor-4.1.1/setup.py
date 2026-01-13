# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stor', 'stor.extensions', 'stor.tests', 'stor.third_party']

package_data = \
{'': ['*'],
 'stor.tests': ['cassettes_py3/TestCanonicalProject/*',
                'cassettes_py3/TestCanonicalResource/*',
                'cassettes_py3/TestCopy/*',
                'cassettes_py3/TestCopyTree/*',
                'cassettes_py3/TestDownloadObjects/*',
                'cassettes_py3/TestExists/*',
                'cassettes_py3/TestGetSize/*',
                'cassettes_py3/TestGlob/*',
                'cassettes_py3/TestList/*',
                'cassettes_py3/TestListDir/*',
                'cassettes_py3/TestLoginAuth/*',
                'cassettes_py3/TestMakedirsP/*',
                'cassettes_py3/TestOpen/*',
                'cassettes_py3/TestRemove/*',
                'cassettes_py3/TestRename/*',
                'cassettes_py3/TestStat/*',
                'cassettes_py3/TestTempUrl/*',
                'cassettes_py3/TestUpload/*',
                'cassettes_py3/TestWalkFiles/*',
                'file_data/*',
                'swift_upload/*',
                'swift_upload/data_dir/*']}

install_requires = \
['boto3>=1.7.0',
 'cached-property>=1.5.1',
 'dxpy>=0.278.0',
 'python-keystoneclient>=1.8.1',
 'python-swiftclient>=3.6.0',
 'requests>=2.20.0']

entry_points = \
{'console_scripts': ['stor = stor.cli:main']}

setup_kwargs = {
    'name': 'stor',
    'version': '4.1.1',
    'description': 'Cross-compatible API for accessing Posix and OBS storage systems',
    'long_description': 'stor\n====\n\n|Build Status|\n\n``stor`` provides a cross-compatible CLI and Python API for accessing\nblock and object storage. ``stor`` was created so you could write one\npiece of code to work with local or remote files, without needing to\nwrite specialized code to handle failure modes, retrying or temporarily\nsystem unavailability. The functional API (i.e., ``stor.copytree``,\n``stor.rmtree``, ``stor.remove``, ``stor.listdir``) will work with the\nsame semantics across all storage backends. This makes it really easy to\ndevelop/test code locally with files and then take advantage of robust\nand cheaper object storage when you push to remote.\n\nView full docs for stor at https://counsyl.github.io/stor/ .\n\nQuickstart\n----------\n\n::\n\n    pip install stor\n\n``stor`` provides both a CLI and a Python library for manipulating Posix\nand OBS with a single, cross-compatible API.\n\nQuickstart - CLI\n----------------\n\n::\n\n    usage: stor [-h] [-c CONFIG_FILE] [--version]\n                {list,ls,cp,rm,walkfiles,cat,cd,pwd,clear,url,convert-swiftstack}\n                ...\n\n    A command line interface for stor.\n\n    positional arguments:\n      {list,ls,cp,rm,walkfiles,cat,cd,pwd,clear,url,convert-swiftstack}\n        list                List contents using the path as a prefix.\n        ls                  List path as a directory.\n        cp                  Copy a source to a destination path.\n        rm                  Remove file at a path.\n        walkfiles           List all files under a path that match an optional\n                            pattern.\n        cat                 Output file contents to stdout.\n        cd                  Change directory to a given OBS path.\n        pwd                 Get the present working directory of a service or all\n                            current directories.\n        clear               Clear current directories of a specified service.\n        url                 generate URI for path\n        convert-swiftstack  convert swiftstack paths\n\n    optional arguments:\n      -h, --help            show this help message and exit\n      -c CONFIG_FILE, --config CONFIG_FILE\n                            File containing configuration settings.\n      --version             Print version\n\nYou can ``ls`` local and remote directories\n\n::\n\n    ›› stor ls s3://stor-test-bucket\n    s3://stor-test-bucket/b.txt\n    s3://stor-test-bucket/counsyl-storage-utils\n    s3://stor-test-bucket/file_test.txt\n    s3://stor-test-bucket/counsyl-storage-utils/\n    s3://stor-test-bucket/empty/\n    s3://stor-test-bucket/lots_of_files/\n    s3://stor-test-bucket/small_test/\n\nCopy files locally or remotely or upload from stdin\n\n::\n\n    ›› echo "HELLO WORLD" | stor cp - swift://AUTH_stor_test/hello_world.txt\n    starting upload of 1 objects\n    upload complete - 1/1   0:00:00 0.00 MB 0.00 MB/s\n    ›› stor cat swift://AUTH_stor_test/hello_world.txt\n    HELLO WORLD\n    ›› stor cp swift://AUTH_stor_test/hello_world.txt hello_world.txt\n    ›› stor cat hello_world.txt\n    HELLO WORLD\n\nQuickstart - Python\n-------------------\n\nList files in a directory, taking advantage of delimiters\n\n.. code:: python\n\n    >>> stor.listdir(\'s3://bestbucket\')\n    [S3Path(\'s3://bestbucket/a/\')\n     S3Path(\'s3://bestbucket/b/\')]\n\nList all objects in a bucket\n\n.. code:: python\n\n    >>> stor.list(\'s3://bestbucket\')\n    [S3Path(\'s3://bestbucket/a/1.txt\')\n     S3Path(\'s3://bestbucket/a/2.txt\')\n     S3Path(\'s3://bestbucket/a/3.txt\')\n     S3Path(\'s3://bestbucket/b/1.txt\')]\n\nOr in a local path\n\n.. code:: python\n\n    >>> stor.list(\'stor\')\n    [PosixPath(\'stor/__init__.py\'),\n     PosixPath(\'stor/exceptions.pyc\'),\n     PosixPath(\'stor/tests/test_s3.py\'),\n     PosixPath(\'stor/tests/test_swift.py\'),\n     PosixPath(\'stor/tests/test_integration_swift.py\'),\n     PosixPath(\'stor/tests/test_utils.py\'),\n     PosixPath(\'stor/posix.pyc\'),\n     PosixPath(\'stor/base.py\'),\n\nRead and write files from POSIX or OBS, using python file objects.\n\n.. code:: python\n\n    import stor\n    with stor.open(\'/my/exciting.json\') as fp:\n        data1 = json.load(fp)\n\n    data1[\'read\'] = True\n\n    with stor.open(\'s3://bestbucket/exciting.json\') as fp:\n        json.dump(data1, fp)\n\nTesting code that uses stor\n---------------------------\n\nThe key design consideration of ``stor`` is that your code should be\nable to transparently use POSIX or any object storage system to read and\nupdate files. So, rather than use mocks, we suggest that you structure\nyour test code to point to local filesystem paths and restrict yourself\nto the functional API. E.g., in your prod settings, you could set\n``DATADIR = \'s3://bestbucketever\'``\\ and when you test, you could use\n``DATADIR = \'/somewhat/cool/path/to/test/data\'``, while your actual code\njust says:\n\n.. code:: python\n\n    with stor.open(stor.join(DATADIR, experiment)) as fp:\n        data = json.load(fp)\n\nEasy! and no mocks required!\n\nRunning the Tests\n-----------------\n\n::\n\n    make test\n\nContributing and Semantic Versioning\n------------------------------------\n\nWe use semantic versioning to communicate when we make API changes to\nthe library. See CONTRIBUTING.md for more details on contributing to\nstor.\n\n.. |Build Status| image:: https://travis-ci.org/counsyl/stor.svg?branch=master\n   :target: https://travis-ci.org/counsyl/stor\n',
    'author': 'Counsyl Inc.',
    'author_email': 'opensource@counsyl.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://counsyl.github.io/stor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
