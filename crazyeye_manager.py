# -*- coding: utf-8 -*-

import sys,os


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s3CrazyEye.settings")
    import django
    django.setup() #这三行可以配置django环境变量，使该python脚本可以使用django数据库

    from backend import main
    interactive_obj = main.ArgvHandler(sys.argv)
    interactive_obj.call()