""" v info v """"""
Name: pyxelist
version: V0.2
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
        self.t=self.turtle.Turtle(visible=False)
        self.t.penup()
        self.t.speed(0)
        return
    def draw(self, frame=0):
        data = self.data if self.type == 'solid' else self.data[frame]
        sx = self.pos[0] - (self.dym[0] * self.size) / 2
        sy = self.pos[1] + (self.dym[1] * self.size) / 2
        self.t.clear()
        self.t.shape("square")
        self.t.shapesize(self.size / 20)
        for row_index, row in enumerate(data):
            for col_index, color in enumerate(row):
                if color == "#======":
                    continue
                self.t.color(color)
                x = sx + col_index * self.size
                y = sy - row_index * self.size
                self.t.goto(x, y)
                self.t.stamp()
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
    AI assistant ChatGPT: helped make it better
"""""" ^ CREDITS ^ """