from django.shortcuts import render,HttpResponse
from django.contrib.auth.decorators import login_required
from Hmt.backends.utils import ArgvManagement
from Hmt.backends.task_detail import HandleCallback
from Hmt.backends.fetch_info import FetchCallbackInfo
from Hmt.backends.create_script import CreateScript
from Hmt.scripts import ftp_upload
import socket,json,threading

def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False
@login_required
def Task(req):
    if req.method == 'POST':
        print(req.POST)
        data = {}
        data['scripte_name'] = req.POST['scripte_name']
        data['user_id'] = req.POST['user_id']
        if req.POST['task_demo']:
            data['demo'] = req.POST['task_demo']
        ip_list =[]
        group_list = []
        ip_group_list = set(str(req.POST['ip_list']).split())
        for ele in ip_group_list:
            if valid_ip(ele):
                ip_list.append(ele)
            else:
                group_list.append(ele)
        data['hosts'] = ip_list
        data['groups'] = group_list
        obj = ArgvManagement(data)
        obj_check = obj.check_data()
        if obj_check:
            error_dic = {}
            error_dic['code'] = 1
            error_dic['info'] = obj_check
            callback_err = json.dumps(error_dic)
            return HttpResponse(callback_err)
        else:
            try:
                ftp_upload.uoload(data['scripte_name'])
            except Exception as e:
                exit('ERROR:the script_file upload ftp_server failure !!!')
            t1 = threading.Thread(target=worker,args=(obj,))
            t1.start()
            success_dic = {}
            success_dic['code'] = 0
            success_dic['info'] = obj.new_task_obj.task_id
            callback_suc = json.dumps(success_dic)
            return HttpResponse(callback_suc)
        # return obj.process()
    return render(req,'Hmt/task.html')

def worker(obj):
    obj.process()

@login_required
def TaskResult(req):
    try:
        if req.GET['task_id']:
            task_id = req.GET['task_id']
            # info =
            return render(req,'Hmt/task_result.html',{'task_id':task_id})
    except Exception as e:
        pass
    # return render(req,'Hmt/task_result.html',{'task_id':req.GET['task_iid']})

@login_required()
def TaskDetail(req):
    if req.method == 'GET':
        task_id = req.GET['task_id']
        task_flag = int(req.GET['flag'])
        if task_id:
            # info = {'code':0,'suc_ips':['1.1.1.1','2.2.2.2','3.3.3.3']}
            init = HandleCallback(task_id,task_flag)
            # info = init.handle1()
            if hasattr(init,'callback_all_ok_list'):
                info = init.handle1()
            elif hasattr(init,'callback_all_no_ok_list'):
                info = init.handle2()
            else:
                info = init.handle3()
            info_json = json.dumps(info)
            return HttpResponse(info_json)
    else:
        return HttpResponse('error')

@login_required
def FetchInfo(req):
    if req.method == 'POST':
        task_id = req.POST['task_id']
        client_ip = req.POST['client_ip']
        fetch_info_obj = FetchCallbackInfo(task_id,client_ip)
        fetch_info = fetch_info_obj.fetch()
        return HttpResponse(fetch_info)

@login_required
def Script(req):
    if req.method == 'POST':
        script_name = req.POST['script_name']
        script_content = req.POST['script_content']
        print(script_name,1111111111111)
        print(type(script_content),2222222222222)
        obj = CreateScript(script_name,script_content)
        print(222222222222222222233333333)
        if obj.check() == 1:
            print(4444444444444444444444)
            return HttpResponse(1)
        else:
            print(555555555555555555555)
            obj.create()
            return HttpResponse(0)
    return render(req,'Hmt/script.html')

@login_required
def Group(req):
    return render(req,'Hmt/group.html')