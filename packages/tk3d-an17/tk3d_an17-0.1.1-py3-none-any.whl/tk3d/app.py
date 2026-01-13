import math

def project(x,y,z,d=400):
    s=d/(d+z); return x*s,y*s

class Cube:
    def __init__(self,s=50):
        self.v=[(-s,-s,-s),(s,-s,-s),(s,s,-s),(-s,s,-s),
                (-s,-s,s),(s,-s,s),(s,s,s),(-s,s,s)]
        self.e=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                (0,4),(1,5),(2,6),(3,7)]
        self.a=0
    def draw(self,cv,cx=200,cy=200):
        p=[]
        for x,y,z in self.v:
            x2=x*math.cos(self.a)-z*math.sin(self.a)
            z2=x*math.sin(self.a)+z*math.cos(self.a)+200
            px,py=project(x2,y,z2)
            p.append((cx+px,cy+py))
        for i,j in self.e:
            cv.create_line(*p[i],*p[j],fill="white")
        self.a+=0.03
