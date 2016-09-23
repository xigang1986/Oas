#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:Alex Li
import os

class BaseSaltModule:
    def __init__(self,sys_argvs,db_models,settings):
        self.db_models = db_models
        self.sys_argvs = sys_argvs
        self.settings = settings

    def process(self):    #接收用户指令时才执行获取主机函数
        self.fetch_hosts()
        self.config_data_dic = self.get_selected_os_type()
    def require(self,*args,**kwargs):
        print("in require ",args,kwargs)
        os_type= kwargs.get('os_type')

        self.require_list = []
        for item in args[0]:
            for mod_name,mod_val in item.items():
                module_obj = self.get_module_instance(base_mod_name=mod_name,os_type=os_type)
                require_condition = module_obj.is_required(mod_name,mod_val)
                self.require_list.append(require_condition)
                #print('require run module:',module_obj)
        #print("require list:",require_list)
    def get_selected_os_type(self):
        data = {}
        for host in self.host_list:
            data[host.os_type] = []
        print('-->data:',data)
        return data
    def fetch_hosts(self):
        '''
        获取主机
        :return:
        '''
        print('--fetching hosts---')
        host_list = []
        if '-h' in self.sys_argvs or '-g' in self.sys_argvs:
            if '-h' in self.sys_argvs:                                              #判断-h参数后主机是否存在
                host_str_index = self.sys_argvs.index('-h') +1
                if len(self.sys_argvs) <= host_str_index:
                    exit("host argument must be provided after -h")
                else: #get the host str
                    host_str = self.sys_argvs[host_str_index]
                    host_str_list = host_str.split(',')
                    host_list += self.db_models.Host.objects.filter(ip__in=host_str_list)
            if '-g' in self.sys_argvs:                                              #判断-g参数后主机组是否存在
                group_str_index = self.sys_argvs.index('-g') +1
                if len(self.sys_argvs) <= group_str_index:
                    exit("host argument must be provided after -h")
                else: #get the host str
                    group_str = self.sys_argvs[group_str_index]
                    group_str_list = group_str.split(',')
                    group_list = self.db_models.HostGroup.objects.filter(name__in=group_str_list)
                    for group in group_list:                                        #列出所有主机组中的主机
                        host_list += group.hosts.select_related()
                    self.host_list = set(host_list)                                 #用set去除重复的主机
                    print(type(host_list))
            print('----host list:', host_list)
            # return True
        else:
            exit("host [-h] or group[-g] argument must be provided")

    def is_required(self,*args,**kwargs):
        exit("Error: is_required() method must be implemented in module class [%s]" % args[0])
    def get_module_instance(self,*args,**kwargs):
        base_mod_name = kwargs.get('base_mod_name')
        os_type = kwargs.get('os_type')
        plugin_file_path = "%s/%s.py" % (self.settings.SALT_PLUGINS_DIR,base_mod_name)          #判断模块名文件是否存在
        if os.path.isfile(plugin_file_path):
            #导入 模块
            module_plugin = __import__('plugins.%s' %base_mod_name)                             #字符串import导入
            special_os_module_name = "%s%s" %(os_type.capitalize(),base_mod_name.capitalize())  #判断出操作系统特有的处理类名称
            module_file= getattr(module_plugin, base_mod_name)                    # 这里才是真正导入模块
            if hasattr(module_file, special_os_module_name):                     #判断有没有根据操作系统的类型进行特殊解析 的类，在这个文件里
                module_instance = getattr(module_file, special_os_module_name)
            else:
                module_instance = getattr(module_file, base_mod_name.capitalize())          #没有则通过通用类解析
            #开始调用 此module 进行配置解析
            module_obj = module_instance(self.sys_argvs,self.db_models,self.settings)
            return module_obj
        else:
            exit("module [%s] is not exist" % base_mod_name)

    def syntax_parser(self,section_name,mod_name,mod_data):
        '''
        解析yaml文件中模块下的数据
        :return:
        '''
        print("-going to parser state data:",section_name,mod_name)
        self.raw_cmds = []
        self.single_line_cmds = []
        for state_item in mod_data:
            print("\t",state_item)
            for key,val in state_item.items():
                if hasattr(self,key):
                    state_func = getattr(self,key)
                    state_func(val,section=section_name)
                else:
                    exit("Error:module [%s] has no argument [%s]" %( mod_name,key ))
        else:           #for循环如果没有break，才会到这里
            if '.' in mod_name:                                     #判断模块是否执行动作
                base_mod_name,mod_action = mod_name.split('.')
                if hasattr(self,mod_action):
                    mod_action_func = getattr(self,mod_action)
                    cmd_list = mod_action_func(section=section_name,mod_data=mod_data) #present
                    data = {
                        'cmd_list':cmd_list,
                        'required_list': self.require_list
                    }
                    if type(cmd_list) is dict:
                        data['file_module'] = True
                        data['sub_action'] = cmd_list.get('sub_action')

                    #上面代表一个section里的具体的一个module 已经解析 完毕了
                    return data

                else:
                    exit("Error:module [%s] has no method [%s]" %( mod_name,mod_action ))
            else:
                exit("Error:module action of [%s] must be supplied" %( mod_name ))