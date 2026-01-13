""" v info v """"""
Name: pyxelist
version: V0.3
"""""" ^ info ^ """

""" v CODE v """
class pyxelist:
    import turtle
    def __init__(self,xpos:int,ypos:int,data:list|dict,size:int,obj_type:str='solid',width:str|int='auto',height:str|int='auto'):
        self.data=data
        self.size=size
        self.type=obj_type
        self.pos=[xpos,ypos]
        if height!='auto'and type(height)!=int:
            try:height=int(height)
            except:height='auto'
        if width!='auto'and type(width)!=int:
            try:width=int(width)
            except:width='auto'
        if type(data) is dict:
            try:
                if height=='auto':height=len(data[next(iter(data))])
                if width=='auto':width=len(data[next(iter(data))][0])
            except Exception as e:print(f'pyxelist error: {e}')
        else:
            if height=='auto':height=len(data)
            if width=='auto':width=len(data[0])
        self.dym=(width,height)
        self.t=self.turtle.Turtle(visible=False)
        self.t.penup()
        self.t.speed(0)
        return
    def draw(self, frame=0):
        data=self.data if self.type=='solid'else self.data[frame]
        sx=self.pos[0]-(self.dym[0]*self.size)/2
        sy=self.pos[1]+(self.dym[1]*self.size)/2
        tss=self.turtle.screensize()
        self.t.clear()
        self.t.shape("square")
        self.t.shapesize(self.size / 20)
        for row_index, row in enumerate(data):
            for col_index, color in enumerate(row):
                if "#======"in color:continue
                gtx = sx + col_index * self.size
                gty = sy - row_index * self.size
                if gtx>tss[0]/2 or gtx<-tss[0]/2 or gty>tss[1]/2 or gty<-tss[1]/2:continue
                try:self.t.color(color)
                except Exception as e:print(f'Color Error:{e}');continue
                self.t.goto(gtx, gty)
                self.t.stamp()
    def set(self,pos:str,by:int|list):
        if pos.lower()=='x':self.pos[0]=by
        elif pos.lower()=='y':self.pos[1]=by
        elif pos.lower()=='both':self.pos=by
        pass
    def move(self,pos:str,by:int|list):
        if pos.lower()=='x':self.pos[0]+=by
        elif pos.lower()=='y':self.pos[1]+=by
        elif pos.lower()=='both':self.pos+=by
""" ^ CODE ^ """

""" v CREDITS v """"""
Developer:
    Github user@yanlin522: created it
    AI assistant ChatGPT: helped make it better
"""""" ^ CREDITS ^ """