#_*_coding:utf-8_*_
import pika
import os,sys,subprocess,urllib2,redis
from hashlib import md5
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import configs
import json,threading
class CommandManagement(object):
    def __init__(self,argvs):
        self.argvs = argvs[1:]
        self.argv_handler()

    def argv_handler(self):
        if len(self.argvs) == 0:
            exit("argument: start\stop")
        if hasattr(self,self.argvs[0]):
            func = getattr(self,self.argvs[0])
            func()
        else:
            exit("invalid argument.")

    def start(self):
        client_obj = Needle()
        client_obj.listen()

    def stop(self):
        pass
class TaskHandle(object):
    def __init__(self,main_obj,task_body):
        self.main_obj = main_obj # Needle object
        self.task_body = json.loads(task_body.decode())

    def processing(self):
        callback_queue = self.task_body['callback_queue']
        callback_data = self.exec_script()
        self.task_callback(callback_queue,callback_data)

    def exec_script(self):
        callback_data = self.task_body['data']
        file_name = callback_data['file_name']
        file_md5 = callback_data['file_md5']
        file_path = '%s/%s'%(configs.FILE_STORE_PATH,file_name)
        print(file_path,333333333333333333333333333)
        print('md5:%s'%file_md5)
        self.redis_conn =redis.Redis(host='192.168.101.200',port=6379,db=0)
        if os.path.exists(file_path):
            local_file_md5 = self.md5(file_path)
            if local_file_md5 == file_md5:
                p=subprocess.Popen("sed -i 's/\r//g' %s; /bin/bash %s"%(file_path,file_path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                p.wait()
                out=str(p.stdout.read())
                err=str(p.stderr.read())
                self.download_file(file_name,file_path)
                print('out1111111111:%s'%out)
                print('err2222222222:%s'%err)
                if p.returncode == 0:
                    out_info=out
                else:
                    if out and err:
                        out_info=out+err
                    elif not out and err:
                        out_info=err
                    elif out and not err:
                        out_info=out
                self.redis_conn.set('TASK_%s_%s_INFO'%(self.task_body['id'],configs.NEEDLE_CLIENT_ID),out_info)
                print(p.returncode)
                #return 'The script_file:[%s] has been executed,result_code:%s'%(file_name,p.returncode)
                if p.returncode == 0:
                    return 0
                else:
                    return 1
            else:
                self.download_file(file_name,file_path)
                local_file_md5 = self.md5(file_path)
                if local_file_md5 == file_md5:
                    p=subprocess.Popen("sed -i 's/\r//g' %s; /bin/bash %s"%(file_path,file_path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    p.wait()
                    out=str(p.stdout.read())
                    err=str(p.stderr.read())
                    self.download_file(file_name,file_path)
                    print('out:%s'%out)
                    print('err:%s'%err)
                    if p.returncode == 0:
                        out_info=out 
                    else:
                        if out and err:
                            out_info=out+err
                        elif not out and err:
                            out_info=err
                        elif out and not err:
                            out_info=out
                    self.redis_conn.set('TASK_%s_%s_INFO'%(self.task_body['id'],configs.NEEDLE_CLIENT_ID),out_info)
                    print (p.returncode)
                    #return 'The script_file:[%s] is not newest, Re-Download and has been executed,result_code:%s'%(file_name,p.returncode)
                    if p.returncode == 0:
                        return 0
                    else:
                        return 1
                else:
                    #return 'The scripts_file:[%s] is no exist in file_server or master not update to file_server!!!'%file_name
                    return 3
        else:
            self.download_file(file_name,file_path)
            local_file_md5 = self.md5(file_path)
            if local_file_md5 == file_md5:
                p=subprocess.Popen("sed -i 's/\r//g' %s; /bin/bash %s"%(file_path,file_path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                p.wait()
                out=str(p.stdout.read())
                err=str(p.stderr.read())
                self.download_file(file_name,file_path)
                print('out:%s'%out)
                print('err:%s'%err)
                if p.returncode == 0:
                    out_info=out 
                else:
                    if out and err:
                        out_info=out+err
                    elif not out and err:
                        out_info=err
                    elif out and not err:
                        out_info=out
                self.redis_conn.set('TASK_%s_%s_INFO'%(self.task_body['id'],configs.NEEDLE_CLIENT_ID),out_info)
                print (p.returncode)
                #return 'The script_file:[%s] has New-Download and has been executed,result_code:%s'%(file_name,p.returncode)
                if p.returncode == 0:
                    return 0
                else:
                    return 1
            else:
                #return 'The scripts_file:%s is no exist in file_server or master not update to file_server!!!'%file_name
                return 3


    def md5(self,file_path):
        m = md5()
        a_file = open(file_path, 'rb')    #需要使用二进制格式读取文件内容
        m.update(a_file.read())
        a_file.close()
        return m.hexdigest()

    def download_file(self,file_name,file_path):
        file_server_addr = configs.FILE_SERVER
        url = 'http://%s/%s'%(file_server_addr,file_name)
        f = urllib2.urlopen(url)
        data = f.read()
        with open(file_path, "wb") as code:
            code.write(data)

    def task_callback(self,callback_queue,callback_data):
        data = {
            'client_id': self.main_obj.client_id,
            'callback_code': callback_data
        }


        self.main_obj.mq_channel.queue_declare(queue=callback_queue)
        #n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
        self.main_obj.mq_channel.basic_publish(exchange='',
                              routing_key=callback_queue,
                              body=json.dumps(data))
        print(" [x] Sent task callback to [%s]" % callback_queue)
class Needle(object):

    def __init__(self):
        self.make_connection()
        self.client_id = self.get_needle_id()
        self.task_queue_name = "TASK_Q_%s" % self.client_id

    def get_needle_id(self):
        #去服务器端取自己的id
        return configs.NEEDLE_CLIENT_ID
    def listen(self):
        #开始监听服务器的call
        self.msg_consume()
    def make_connection(self):
        print('make1111111111111')
        #self.mq_conn = pika.BlockingConnection(pika.ConnectionParameters(
        #               configs.MQ_CONN['host']))
        #self.mq_channel = self.mq_conn.channel()
        credentials = pika.PlainCredentials('asdf', '123456')
        # self.mq_conn = pika.BlockingConnection(pika.ConnectionParameters(
        #                configs.MQ_CONN['host'],port=settings.MQ_CONN['port'],))
        parameters = pika.ConnectionParameters(configs.MQ_CONN['host'],5672,'/',credentials)
        connection = pika.BlockingConnection(parameters)
        self.mq_channel = connection.channel()

    def publish(self,data):
        print('\033[41;1m-----going to publish msg ------\033[0m',data)


        self.mq_channel.queue_declare(queue='hello')
        self.mq_channel.basic_publish(exchange='',
                              routing_key='hello',
                              body='Hello World!')
        print(" [x] Sent 'Hello World!'")
        self.mq_conn.close()

    def msg_callback(self,ch, method, properties, body):
        print(" [x] Received a task msg " )
        thread = threading.Thread(target=self.start_thread,args=(body,))
        thread.start()
        print(" [x] Received %r" % (body,))
    def start_thread(self,task_body):
        print('\033[31;1m start a thread to process task\033[0m')
        task = TaskHandle(self,task_body)
        task.processing()
    def msg_consume(self):
        '''
        dsfdsf胜多负少get task callback
        :return:
        '''
        print('consume222222222')
        self.mq_channel.queue_declare(queue=self.task_queue_name,arguments={'x-message-ttl': 50000})
        self.mq_channel.basic_consume(self.msg_callback,
                              queue=self.task_queue_name,
                              no_ack=True)

        print(' [%s] Waiting for messages. To exit press CTRL+C' % self.task_queue_name)
        self.mq_channel.start_consuming()
