from Oas import settings
import os,sys

class CreateScript():
    def __init__(self,script_name,script_content):
        self.script_name = script_name
        self.script_content = script_content
        self.script_path = settings.SCRIPTS_DIR

    def check(self):
        if os.path.exists('%s/%s'%(self.script_path,self.script_name)):
            print(os.path.exists('%s/%s'%(self.script_path,self.script_name)),656565)
            return 1

    def create(self):
        f = open('%s/%s'%(self.script_path,self.script_name),'w')
        f.write(self.script_content)
        f.close()

