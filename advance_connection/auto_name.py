from util_with_json import *
import asyncio
C=ControlA()

def name_iterator(name_list,preferred_name=None):
    def name_yielder():
        if preferred_name is not None:
            yield preferred_name
        yield from range(int(10e5))
    
    for i in name_yielder():
        i=str(i)
        if i not in name_list:
            return i


def names(C,S,topic,payload):
    if not topic=="requests_all":return
    if not payload=="names":return
    C.publish("names",S.names)
    return True
    
C.requests_func_list.append(names)


async def task_1(C,S):
    
    
    #1: request others name and record name (ask everyone?)
    C.subscribe("names")
    C.subscribe("lastwill")

    C.publish("requests_all","names")
    # get_others requested name
    li=None
    while li is None:
        await asyncio.sleep(0.1)
        li=C.pipeline_checker("names")
    
    dic={}
    haved_len=0
    for i in range(len(li)):
        di=li.popleft()
        dic.update(di)
        if haved_len!=len(di):
            if haved_len==0:
                haved_len=len(di)
            else:
                print("not identical name dict, should be error")
                print(lii,haved_len)
                print("="*20)
    S.names=dic
    return True
    
def remove_name(C,S,topic,payload):
    if not topic=="lastwill":return
    print("grieving")
    # somehow not json
    name=str(payload)
    try:S.names.pop(name)
    except KeyError:
        print("not_supposed")
    return True

def record_names(C,S,topic,payload):
    if not topic=="name":return
    print("let's GO")
    name=payload
    
    if tuple(name.values())[0] in S.names.values():
        C.publish(S.name,"name already taken")
        print(name)
        if name == S.name:
            C.publish(S.name,"That Is My Name")
            print("my name run in to confict")
    else:S.names.update(name)
    return True
    
C.requests_func_list.extend([record_names,remove_name])


async def task_2(C,S,preferred_name):
    import time
    #2: generate its own name, publish it to let others confirm there is no conflicts
    C.subscribe("requests_all")
    S.name=name_iterator(S.names.values(),preferred_name)
    S.name_time=time.time()
    S.names.update({C.id_name:S.name})
    

    await asyncio.sleep(0.1)
    
    #3: one own channel is created, for reciving data.
    C.publish(S.name,"I should be first and only.")
    C.subscribe(S.name)
    
    await asyncio.sleep(0.1)
    
    return True
    
    
def respond_names(C,S,topic,payload):
    if not hasattr(S,"name"):return
    if not topic==S.name:return
    # if not topic=="name":return
    thing=payload
    if thing=="I should be first and only.":print("that is a big error")
    print("that should be my channel?")
    return True
    
C.requests_func_list.append(respond_names)

async def task_3(C,S):
    #3:  if confilct, random a number to wait on their "own" chanel, and claim it as its own. the other start from 1.
    import random
    for i in range(3):
        await asyncio.sleep(random.randint(1,100)*0.001)
        li=C.pipeline_checker("name")
        if not li:break
        print(li)
        print("TODOTODOTODO")
    
    else:
        print("bad_luck")
    
    if li:
        return False
    
    C.publish("name",{C.id_name:S.name})
    C.subscribe("name")
    
    await asyncio.sleep(0.1)
    return True
    
    
    
     
def hihi(C,S,topic,payload):
    if not topic=="hihi":return
    return True
C.pipeline.func_list=[hihi,]

def recv_data(C,S,topic,payload):
    if not hasattr(S,"name"):return
    if not topic.startswith(S.name):return
    topic=topic.replace(S.name,"",1)
    topic=topic.replace("/","",1)
    for func in S.func_list:
        ret=func(C,S,topic,payload)
        if ret==None:continue
        return ret
    
C.requests_func_list.append(recv_data)


async def task_4(C,S):
    #3:  if no confilct, json format reading.
    C.subscribe(S.name+"/#")
    #4: in their own channel, when other want to send some special message like raw data, new channels are created.
    
    return True
    
    
class StateMachine:
    def __init__(self,):
        ...
    def state(self,):
        ...
    def next_step(self,):
        ...
    
    
    
async def await_tasks(C,preferred_name=None):
    S=C.pipeline
    first=True
    while 1:
        if not first:print("TODO~!!!,need to clear pipeline if need to restart")
        first=False
        if not await task_1(C,S):continue
        if not await task_2(C,S,preferred_name):continue    
        if not await task_3(C,S):continue    
        if not await task_4(C,S):continue
        break
    return True
    
    
from collections import deque;ret=deque((),1)
def exec_ret(C,S,topic,payload):
    global ret
    if not topic=="exec":return
    print("doing exec")

    # designed not to use too often
    
    if "ret" in payload:
        print("using 'ret' causes problem, skipping")
        return True
        
    to_ret=False
    if not "=" in payload:
        payload=f"ret.append({payload})"
        to_ret=True
        
    try:
        exec(payload)
        if to_ret:
            try:
                g=ret.popleft()
                try:
                    C.publish("ret_"+S.name+"/"+"exec",g)
                except:
                    C.publish("ret_"+S.name+"/"+"exec",str(g))
            except IndexError:g=None
    except Exception as e:
        C.publish("ret_"+S.name+"/"+"exec","error"+str(e))
        return True
    
    return True


C.pipeline.func_list.append(exec_ret)
    



