import pika,json,time,threading,ctypes,inspect,redis  #先导入django的app，这样才能导入相关模块和配置
#django.setup()
from Hmt import models
from Oas import settings
class TaskHandle(object):
    '''
    generate task
    '''
    def __init__(self,task_data,module_obj):
        self.task_data = task_data
        self.module_obj = module_obj #哪个模块调用我。这个变量就是谁
        self.make_connection()
        self.apply_new_task()
        self.callback_list = []

    def apply_new_task(self):
        '''
        create a task record in db and return the task id
        :return:
        '''
        new_task_obj = models.Task(user_id=self.module_obj.data['user_id'])
        new_task_obj.save()
        print(new_task_obj.datetime,11111111111111111111111111111111111)
        self.send_list = []
        for host in self.module_obj.host_list:
            self.send_list.append(host.ip)
        self.task_id = new_task_obj.id
        redis_conn =redis.Redis(host=settings.REDIS_CONN['host'],port=settings.REDIS_CONN['port'],db=0)
        redis_conn.set('TASK_CALLBACK_%s_HOST_LIST'%self.task_id,json.dumps(self.send_list))

    def _async_raise(self,tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self,thread):
        self._async_raise(thread.ident, SystemExit)
    def dispatch_task(self):
        '''
        format the task data and make it ready to sent
        :return:
        '''
        print('send task to :',self.module_obj.host_list)
        self.callback_queue_name = "TASK_CALLBACK_%s" % self.task_id
        data = {
            'data':self.task_data,
            'id': self.task_id,
            'callback_queue': self.callback_queue_name,
            'token':None
        }

        print("-------task data --------")
        print(self.task_data)
        print("-------end task data --------")

        for host in self.module_obj.host_list:
            self.publish(data,host)

        #开始等待任务结果:
        flag = 0
        self.callback_num = 0
        while flag < 5:
            t1 = threading.Thread(target=self.wait_callback)
            t1.start()
            time.sleep(2)
            self.stop_thread(t1)
            flag += 1
            if self.callback_num == len(self.module_obj.host_list):
                self.close_connection()
                redis_conn = redis.Redis(host=settings.REDIS_CONN['host'], port=settings.REDIS_CONN['port'], db=0)
                redis_conn.set('TASK_CALLBACK_%s_ALL_OK'%self.task_id,json.dumps(self.callback_list))
                break
            elif flag == 5:
                redis_conn = redis.Redis(host=settings.REDIS_CONN['host'], port=settings.REDIS_CONN['port'], db=0)
                if self.callback_list:
                    redis_conn.set('TASK_CALLBACK_%s_ALL_NO_OK'%self.task_id,json.dumps(self.callback_list))
                else:
                    redis_conn.set('TASK_CALLBACK_%s_ALL_NO_OK'%self.task_id,"is_none")

    def make_connection(self):
        print('settings mq',settings.MQ_CONN )
        credentials = pika.PlainCredentials(settings.MQ_CONN['user'], settings.MQ_CONN['password'])
        # self.mq_conn = pika.BlockingConnection(pika.ConnectionParameters(
        #                settings.MQ_CONN['host'],port=settings.MQ_CONN['port'],))
        parameters = pika.ConnectionParameters(settings.MQ_CONN['host'],settings.MQ_CONN['port'],'/',credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.mq_channel = self.connection.channel()

    def publish(self,task_data,host):
        print('\033[41;1m-----going to publish msg ------\033[0m;\n')

        #声明queue
        queue_name = 'TASK_Q_%s' %host.id
        # self.mq_channel.queue_declare(queue=queue_name,arguments={'x-message-ttl': 50000})
        self.mq_channel.queue_declare(queue=queue_name)

        print(json.dumps(task_data).encode())

        #n RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange.
        self.mq_channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body= json.dumps(task_data))
        print(" [x] Sent task to queue [%s] 'Hello World!'" % queue_name)

    def close_connection(self):
        self.connection.close()

    def task_callback(self,ch, method, properties, body):
        print(body)
        callback_info = json.loads(body.decode())
        redis_conn = redis.Redis(host=settings.REDIS_CONN['host'],port=settings.REDIS_CONN['port'],db=0)
        redis_conn.rpush('TASK_CALLBACK_%s'%self.task_id,body)
        print(redis_conn.lrange('TASK_CALLBACK_%s'%self.task_id,start=0,end=-1),353535353535353)
        self.callback_list.append(callback_info)
        self.callback_num+=1
        # print(self.callback_list)
        #time.sleep(3)
        #self.mq_channel.stop_consuming()

    def wait_callback(self):
        '''
        get task callback
        :return:
        '''
        #print('------waiting for callback from :' ,self.callback_queue_name)

        self.mq_channel.queue_declare(queue=self.callback_queue_name)

        self.mq_channel.basic_consume(self.task_callback,
                              queue=self.callback_queue_name,
                              no_ack=True)

        print('\033[44;1m[%s] Waiting for callback. To exit press CTRL+C\033[0m' % self.callback_queue_name)
        self.mq_channel.start_consuming()