#_*_coding:utf-8_*_


import sys,os


if __name__ == "__main__":
    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(BASEDIR)
    from core import sanshi
    sanshi.CommandManagement(sys.argv)
