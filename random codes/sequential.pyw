import os
import matplotlib.pyplot as plt
import numpy as np
import random

#write random sunspots to txt file
"""with open("C:\\Users\\code\\Desktop\\plotting\\sunspots.txt", 'a') as f:
    for month in range(1,1200):
        snum = random.randint(5, 200)
        f.write("\n%s %s"%(month,snum))"""
with open(os.path.expanduser("~\\Desktop\\plotting\\sunspots.txt")) as txt:#automatically closes file
    data = txt.readlines()#returns a list which is assigned to variable data 
    month = [] #months initialized to an empty list data type
    sunspots_num = []
    for element in data: #loops through all the elements in list
        if element != "\n": #executes if the element is not an empty line, else continues
            month.append(int(element.strip('\n').split()[0]))#strip the nextline(\n),
            #remove empty space and get first element of the list returned appended to list of months
            sunspots_num.append(float(element.strip('\n').split()[1]))#get the second element assigned to sunspots number
fig, ax = plt.subplots()
ax.set_title("Sunspots against Months")#Graph title
ax.plot(month,sunspots_num,linewidth=1)#plot the two lists, sunspots against month
plt.axis([0,1000,0,200])#set axis limits [xmin,xmax,ymin,ymax] Displays first 1000 data points
start, end = ax.get_xlim()
plt.xticks(np.arange(start,end,50))#set x interval of 50
ystart, yend = ax.get_ylim()
plt.yticks(np.arange(0,yend,10))#set y interval of 10
ax.set(xlabel="Number of Months",ylabel="Number of Sunsposts")#x and y labels
ax.grid()
plt.gcf().autofmt_xdate()#auto format the x axis
plt.show()

        

