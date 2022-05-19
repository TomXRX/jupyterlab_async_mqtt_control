class Control:    
    def __init__(self,mqtt_config=("mqtt",1883,("tom","xiao"))):
        self.HOST,self.PORT,self.client_pw=mqtt_config
        self.client=self.client_start()
        self.client.loop_start()
    
    def client_start(self):
        import time
        import paho.mqtt.client as mqtt
        name=str(time.time())
        client = mqtt.Client(name)
        self.id_name=name
        client.username_pw_set(*self.client_pw)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.will_set('lastwill', name)
        client.connect(self.HOST, self.PORT, 60)
        return client

    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        
    def __call__(self,*args):
        self.publish(*args)
                
    # result=deque((),10)
    #TODO: possible too_much
    #to not flood result_keeper with too much out-dated info
    def on_message(self,client, userdata, msg):
        print(msg.payload)
        # self.result.append(msg.payload)
        
    def pop_result(self):
        try:return self.result.popleft()
        except:pass
    
from collections import defaultdict,deque
class ExecPipeline:
    state_dict=defaultdict(deque)
        
    def add_thing(self,topic,data):
        self.state_dict[topic].append(data)
        
    #TODO:be aware of the list too big.
        
    # async def
        #with payload
    
    def __call__(self,*args):
        self.add_thing(*args)

class ControlAdvance(Control):
    def __init__(self,*args,pipeline=None,**kwargs):
        if pipeline is None:pipeline=ExecPipeline()
        self.pipeline=pipeline
        super().__init__(*args,**kwargs)
    
    def on_message(self,client,userdata,msg):
        self.pipeline(msg.topic,msg.payload)
        
from functools import wraps
import asyncio

def loop(t=0.001):
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            import asyncio
            while 1:
                await asyncio.sleep(t)
                ret=await func(*args, **kwargs)
                if ret:break
            return
        return wrapped
    return wrapper

import asyncio
def try_loop(t=0.001,skip_errors=(),jump_errors=(asyncio.CancelledError,KeyboardInterrupt)):
    def wrapper(func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            while 1:
                await asyncio.sleep(t)
                try:
                    ret=await func(*args, **kwargs)
                    if ret:break
                except tuple(jump_errors):
                    return
                except tuple(skip_errors):
                    pass
                except Exception as e:
                    print("")
                    print(e)
                    print("continue running")
            return
        return wrapped
    return wrapper