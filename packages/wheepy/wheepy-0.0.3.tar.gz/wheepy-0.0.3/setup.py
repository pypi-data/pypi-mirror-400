from setuptools import setup

f = open('./README.md', 'r')
long_description = f.read()
f.close()

setup(
        name='wheepy',
        version='0.0.3',
        description='Unified interface to key value with locking and transactions.',
        author='Louis Holbrook',
        author_email='dev@holbrook.no',
        license='WTFPL',
        long_description=long_description,
        long_description_content_type='text/markdown',
        extras_require={
            'couchdb': ['couchdb~=1.2'],
            'valkey': ['valkey~=6.1.1'],
        },
        packages=[
            'whee',
            'whee.couchdb',
            'whee.valkey',
        ],
        url='https://holbrook.no/src/whee/',
        )
