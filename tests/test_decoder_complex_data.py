#!/usr/bin/env python
# coding=utf-8
"""
source: https://en.wikipedia.org/wiki/YAML#Basic_components_of_YAML
"""
from __future__ import absolute_import

from textwrap import dedent

import pureyaml
from tests.utils import test_dir


def load(text):
    obj = pureyaml.load(text)
    return obj


def test_travis_yml():
    # noinspection SpellCheckingInspection
    secure_block = (  # :off
        'ndFpfTvPZN8SfvduvS4567k1TqYl7L7lRxxEPjmRzg3OgzMgCHRMO/uCrce5i8TkxTWL'
        'W82ArNvBZnTkRzGyChKfoNzKwukgrJACOibc6cPgNBPpuDpZTb7X6hZixSs9VBsMwL9T'
        'kQfImq3Q2uSnW7tBrHYKEIOXeCmKzomI3RYxWoxOlrAP7TqUjxyw/Ax5pOdjODDEMOjB'
        'Z8qRcrRD/n/JyAQrNVtaEaMkauTPbvJ86vG8mDPLzD3c2PFK1qAOimcJb5izM9y9kent'
        '/muLfjeruBxwYGrqAkQnWM0KUqMbfZ9sxMO0hgMZs3p2fldTyANC9bRu65XLW3qseHs9'
        'NTbbdgAZMlsXU9WxzvxTyibvMGHODyps/Ra9NkgRZJC9NLsabuw42P3AVfQjhih/dwn0'
        'DjRU+DlNyY291CazPjSWP4hLBAp72hhv1sGQD33sY3ERx5XPXyeb1B32s3l94bpdPwzO'
        'Hf3MIHAs4Uj32mToi0699lp749PQ4o0Jb2WF0P8vh+vlOJNVM+51vO5CmEj2cF7rJcrb'
        'n+T68gmlvqcYCt3q5gCn+4iBhzGCqeDxlDU1jgC9T/9V4Q+qyAEv/wtYDduoe4R1WGWO'
        'lqSxr8k6Tr92CjI1TXbJUP3N3V0pNYayUJDIIvjWy7T/10xRhMaRhBM88XDJh7QBpcZT'
        'KJo='
    )  # :on
    text = dedent("""
        # This file was autogenerated and will overwrite each time you run travis_pypi_setup.py
        env:
        - TOXENV=py26
        - TOXENV=py27
        - TOXENV=py33
        - TOXENV=py34
        - TOXENV=py35
        - TOXENV=pypy
        - TOXENV=docs
        install:
        - pip install tox coveralls
        language: python
        python:
        - '3.5'
        script:
        - tox -e $TOXENV
        after_success:
        - coveralls
        deploy:
          true:
            condition: $TOXENV == py34
            repo: bionikspoon/pureyaml
            tags: true
          distributions: sdist bdist_wheel
          password:
            secure: {secure_block}
          provider: pypi
          user: bionikspoon

    """)[1:].format(secure_block=secure_block)

    expected = {  # :off
        'env': [
            'TOXENV=py26',
            'TOXENV=py27',
            'TOXENV=py33',
            'TOXENV=py34',
            'TOXENV=py35',
            'TOXENV=pypy',
            'TOXENV=docs'
        ],
        'language': 'python',
        'script': ['tox -e $TOXENV'],
        'python': ['3.5'],
        'after_success': ['coveralls'],
        'install': ['pip install tox coveralls'],
        'deploy': {
            True: {
                'repo': 'bionikspoon/pureyaml',
                'condition': '$TOXENV == py34',
                'tags': True
            },
            'password': {
                'secure': secure_block
            },
            'distributions': 'sdist bdist_wheel',
            'user': 'bionikspoon',
            'provider': 'pypi'
        }
    }  # :on

    actual = load(text)
    assert actual == expected

    travis_yml = test_dir('assets', '.travis.yml')

    with open(travis_yml) as f:
        actual = pureyaml.load(f)

    assert actual == expected
