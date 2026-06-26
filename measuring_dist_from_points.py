import pandas as pd

from PIL import ImageFont
from PIL import ImageDraw
import itertools
import array
from metfun import *

import pickle

import os
import csv


ProjDir = input('Hello there! Please, input the full address of the directory where the map images are located. For example, "c:\\Users\\username\\Desktop\\projfolder\\"... ')

os.chdir(ProjDir)

MapFileName = input('Input the name of the .pkl file (without extension): ')

MaxNumOfEntrances = 1

OutputData = {"cave/bunkeri": [], "Bat N" : [], "Distance" : []}




############### Getting the coordinates

assert os.path.isfile(MapFileName+'.xlsx'), "there is no file with coordinates"
CoordFile = pd.read_excel(MapFileName+'.xlsx')
Bats = []
for i in range(len(CoordFile["first coordinate"])):
    Bats.append([int(CoordFile["first coordinate"][i]), int(CoordFile["second coordinate"][i])])


############### Getting the picture in 'npy format and 
############### all the precomputed data from the .pkl file

toDrawTraj = input('Do you want me to draw trajectories to bats? Type y/n: ')

with open("Pickles\\"+MapFileName+".pkl", 'rb') as file:
    SavedData = pickle.load(file)
data = SavedData['data']
MaxNumOfEntrances = SavedData['MaxNumOfEntrances']
entrances = SavedData['entrances']
isinside = SavedData['isinside']
bdry = SavedData['bdry']
dist = SavedData['dist']
traj = SavedData['traj']
scale = SavedData['scale']
scale_line = SavedData['scale_line']

shape = data.shape


############### Checking if all the bats are inside the map area 
############### and moving them inside if needed

for i in range(len(Bats)):
    if not isinside[Bats[i][0], Bats[i][1]]:
        print(f"Bat {i+1} is not inside, it will be moved")

Bats = [find_nearest_inside(data, isinside, v) for v in Bats]


############### Computing the distances from the points

Bat_entrance = []
for v in Bats:
    i = 0
    d = dist[0][v[0],v[1]]
    for k in range(len(entrances)):
        if d > dist[k][v[0],v[1]]:
            i = k
            d = dist[k][v[0],v[1]]
    Bat_entrance.append(i)

for i in range(len(Bats)):
    OutputData["cave/bunkeri"].append(MapFileName)
    OutputData["Bat N"].append(i+1)
    OutputData["Distance"].append(round(dist[Bat_entrance[i]][Bats[i][0], Bats[i][1]]*scale, 3))


############### draw trajectories if needed
if toDrawTraj == 'y':
    for i in range(len(Bats)):
        point = Bats[i]
        while traj[Bat_entrance[i]][point[0], point[1]]:
            for j in line(point, traj[Bat_entrance[i]][point[0], point[1]], data):
                data[j[0],j[1]] = [255,0,0]
            point = traj[Bat_entrance[i]][point[0], point[1]]


############### highlight bats on the picture

for v in Bats:
    for w in ball(v[0], v[1], 3):
        if inrange(data, w):
            data[w[0], w[1]] = [100,10,100]

############### creating file edited_...
Image.fromarray(data).save('edited_' + MapFileName + '.jpg')
img = Image.open('edited_' + MapFileName + '.jpg')
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('arial.ttf', 40)

for i in range(len(Bats)):
    draw.text((Bats[i][1], Bats[i][0]), str(i+1), (100,10,100), font=font)

############### saving the output

img.save('edited_' + MapFileName + '.jpg')


pd.DataFrame(OutputData).to_excel(MapFileName+"_distances.xlsx", index=False)


print('finished!')
