import os,sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Oas.settings")           #将django的settings配置加入环境变量
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)                                                   #将Oas加入到python环境变量
    from Hmt.backends.utils import ArgvManagement
    obj = ArgvManagement(sys.argv)
    print(obj.process())
