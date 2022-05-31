from util import *
from collections import defaultdict,deque
import asyncio
class ControlA(ControlAdvance):    
    def pipeline_checker(self,topic):
        return self.pipeline.state_dict[topic]
    
    @loop()
    async def pipeline_caller(self):
        if self.new_message<=0:return
        self.new_message-=1
        for key,item in self.pipeline.state_dict.items():
            try:i=item.popleft()
            except:continue

            ret=self.requests_all(key,i)
            if ret is None:
                if key=="names":continue
                print(f"request not handled {str(i)}")
                item.append(i)
                await asyncio.sleep(0.1)

    requests_func_list=list()
    def requests_all(self,topic,payload):
        for func in self.requests_func_list:
            #(C,S,t,p)            
            # TODO: ?try more error?
            try:
                ret=func(self,self.pipeline,topic,payload)
            except AttributeError:pass
            if ret is None:continue
            return ret
    
    class Channel:
        json=True
        auto_define=True
        sended=False
        # pickle=True
        # pickle is inconsistent in micropython, kind of defeat the purpose.
        def set_json(self,j=True):
            self.auto_define=False
            self.json=j
    
    debug=False
    sended_warned=0
    channels=defaultdict(Channel)
    new_message=0
    def on_message(self,client,userdata,msg):
        
        topic=msg.topic
        payload=msg.payload

        if self.debug:print(f"Have a message that is ({topic},{payload})")
        if self.do_not_hear_itself_publish(topic,payload):return
        if self.debug:print("is recieved")
        
        channel=self.channels[topic]
        
        if channel.auto_define and not self.sended_warned and not channel.sended:
            print("impossible to auto_define without sending data first")
            self.sended_warned=1
            
        self.new_message+=1
        
        # if channel.pickle:
            # import pickle
            # payload=pickle.loads(payload)
            # return self.pipeline(topic,payload)    
        if channel.json:
            import json
            try:payload=json.loads(payload.decode())
            except:
                try:payload=payload.decode()
                except:
                    print("bad payload")
                    return
            return self.pipeline(topic,payload)
        return self.pipeline(topic,payload)
        
    subscribed=list()
    def subscribe(self,topic:str):
        self.client.subscribe(topic)
        return self.subscribed.append(topic)
        
    pop_next_recv=list()
    def do_not_hear_itself_publish(self,topic,payload):
        #I mean, if you subscribe to a channel contians itself.
        #being able to send in that channel is hard.(without bringing a long self id)
        tu=(topic,payload)
        if not tu in self.pop_next_recv:return
        #do not go through pipeline (state_saver). handle all by itself.
        
        self.pop_next_recv.remove(tu)
        
        if len(self.pop_next_recv)>10:
            print(f"self.pop_next_recv too long, {self.pop_next_recv}")
            self.pop_next_recv=[]
        return True
        
        
        
    def publish(self,topic,payload):
        def json_transform(payload):
            import json
            return json.dumps(payload).encode()
        
        # def pickle_transform(payload):
            # import pickle
            # return pickle.dumps(payload)
        
        channel=self.channels[topic]
        
        if channel.auto_define and not channel.sended:
            channel.json=not payload is bytes
            
        

        # if channel.pickle:
            # payload=pickle_transform(payload)
        if channel.json:
            payload=json_transform(payload)
        
        if topic in self.subscribed:
            self.pop_next_recv.append((topic,payload))
            
        self.client.publish(topic,payload)
        
        channel.sended=True
        
        