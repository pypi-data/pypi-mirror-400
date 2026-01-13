""" v info v """"""
Name: pyxelist
version: V0.1
"""""" ^ info ^ """

""" v CODE v """
class pyxelist:
    import turtle
    def __init__(self,xpos:int,ypos:int,data:list|dict,size:int,obj_type:str='solid',width:str|int='auto',height:str|int='auto'):
        self.data=data
        self.size=size
        self.type=obj_type
        self.pos=(xpos,ypos)
        if height=='auto':height=len(data)
        if width=='auto':width=len(data[0])
        self.dym=(width,height)
        self.t=pyxelist.turtle
        self.t.hideturtle()
        self.t.penup()
        self.t.tracer(0)
        return
    def draw(self,frame=0):
        sx=round(self.pos[0]-self.dym[0]*self.size/2)
        sy=round(self.pos[1]+self.dym[1]*self.size/2)
        self.t.goto(sx,sy)
        self.t.setheading(0)
        if self.type=='solid':
            nl_loop=0
            for list in self.data:
                self.t.goto(sx,sy-nl_loop*self.size)
                for color in list:
                    if color=='#======':pass
                    else:self.t.color(color),self.t.begin_fill()
                    for side in range(4):
                        self.t.forward(self.size)
                        self.t.right(90)
                    if color!='#======':self.t.end_fill()
                    self.t.forward(self.size)
                nl_loop+=1
            pass
        elif self.type=='animated':
            nl_loop=0
            for list in self.data[frame]:
                self.t.goto(sx,sy-nl_loop*self.size)
                for color in list:
                    if color=='#======':pass
                    else:self.t.color(color),self.t.begin_fill()
                    for side in range(4):
                        self.t.forward(self.size)
                        self.t.right(90)
                    if color!='#======':self.t.end_fill()
                    self.t.forward(self.size)
                nl_loop+=1
            pass
        self.t.update()
        return
    def set(self,pos:str,by:int|tuple):
        if pos.lower()=='x':
            self.pos[0]=by
            pass
        elif pos.lower()=='y':
            self.pos[1]=by
            pass
        elif pos.lower()=='both':
            self.pos=by
            pass
        pass
    def move(self,pos:str,by:int|tuple):
        if pos.lower()=='x':
            self.pos[0]+=by
            pass
        elif pos.lower()=='y':
            self.pos[1]+=by
            pass
        elif pos.lower()=='both':
            self.pos+=by
            pass
        pass
    pass
""" ^ CODE ^ """

""" v CREDITS v """"""
Developer:
    Github user@yanlin522: created it
"""""" ^ CREDITS ^ """