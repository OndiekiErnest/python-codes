# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
import numpy as np
from tkinter import *
import random
import colorsys

from PIL import ImageGrab

def colorT(c):
    return '#%02x%02x%02x' % tuple(c)

class pendulum:
    def __init__(self,d,alpha,x0,y0,c):
        self.fix_x = x0
        self.fix_y = y0
        self.length = d
        self.angle = [alpha, alpha]
        self.pos = np.zeros(2)
        self.getpos()

        self.m=1000.
        self.g=9.81
        self.damp = 0.999
        self.dt=0.01
        self.color=colorT(c)
        self.cv_dot=None
        self.cv_lin=None

    def getpos(self):
        self.pos[0] =  self.length*np.sin(self.angle[0])+self.fix_x
        self.pos[1] =  self.length*np.cos(self.angle[0]) +self.fix_y

    def newAngle(self):
        self.angle[1] +=  self.dt *(-self.m*self.g/self.length*np.sin(self.angle[0]))
        self.angle[0] += self.angle[1]*self.dt

class MyApp(Tk):
    def __init__(self):
        self.nbi=0


        Tk.__init__(self)
        fr = Frame(self)
        fr.pack()
        width = 1288
        height = 728
        self.canvas  = Canvas(fr, height = height, width = width,bg= 'black')
        self.canvas.pack()

        self.fix = (width/2,0)
        self.p=[]
        l=600
        m=20#m=30
        c=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.r=8
        for i in np.arange(40):
            self.p.append(pendulum(l,-np.pi/4,1280/2,0,c))
            l-=m
            m*=0.96#0.95


        for i in np.arange(len(self.p)):
            self.p[i].cv_lin =self.canvas.create_line(self.fix[0], self.fix[1],self.p[i].pos[0], self.p[i].pos[1], width=1, fill=colorT((100,100,100)))
            self.p[i].cv_dot =self.canvas.create_oval(self.p[i].pos[0]-self.r, self.p[i].pos[1]-self.r,self.p[i].pos[0]+self.r, self.p[i].pos[1]+self.r )
            self.canvas.itemconfig(self.p[i].cv_dot, outline=self.p[i].color)
            self.canvas.itemconfig(self.p[i].cv_dot, fill=self.p[i].color)
        self.update()

    def update(self ):
        h=colorsys.hsv_to_rgb(np.mod(self.nbi,1000.)/1000., 1., 1.)
        c =colorT((int(h[0]*255),int(h[1]*255),int(h[2]*255)))

        for p_ in self.p:
            p_.newAngle()
            p_.getpos()
            p_.color =c
            self.canvas.itemconfig(p_.cv_dot, outline=p_.color)
            self.canvas.itemconfig(p_.cv_dot, fill=p_.color)
            # self.canvas.itemconfig(p_.cv_lin, fill=p_.color)
            self.canvas.coords(p_.cv_dot,p_.pos[0]-self.r, p_.pos[1]-self.r,p_.pos[0]+self.r, p_.pos[1]+self.r )
            self.canvas.coords(p_.cv_lin, self.fix[0], self.fix[1],p_.pos[0], p_.pos[1])

        self.canvas.update()
        self.nbi+=1

        return
if __name__ == "__main__":
    root = MyApp()
    i=0
    while 1:
        root.update( )
        root.after(50)