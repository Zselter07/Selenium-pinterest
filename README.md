# selenium_pinterest
![python_version](https://img.shields.io/static/v1?label=Python&message=3.5%20|%203.6%20|%203.7&color=blue)

## Install
~~~~shell
pip install --upgrade selenium-pinterest
# or
pip3 install --upgrade selenium-pinterest
~~~~

## Usage
~~~~python

from selenium_pinterest import Pinterest

pinterest_demo = pinterst_one = Pinterest("/path/to/cookies", "path/to/extension", host = 'host_nr', port=12345)
pinterest_demo.repin('pin_id')

## Dependencies
geckodriver
