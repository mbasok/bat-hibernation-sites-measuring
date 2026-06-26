from PIL import Image
import pandas as pd
import numpy as np
from math import sqrt
from PIL import ImageFont
from PIL import ImageDraw
import itertools
import array
import time

from metfun import *

import pickle

import os
import csv


ProjDir = input('Hello there! Please, input the full address of the directory where the map images are located. For example, "c:\\Users\\username\\Desktop\\projfolder\\"... ')

os.chdir(ProjDir)


FORMAT = input('Input the format of the map images (jpg or png): ')

MaxNumOfEntrances = 1

OutputData = {"cave/bunkeri": [], "Area" : [], "Perimeter" : [], "distance" : []}

for MapFileName in [os.path.splitext(x)[0] for x in os.listdir() if x.endswith('.'+FORMAT) ]:

    start_time0 = time.time()

    #ignore files started with edited_

    if MapFileName[:7] == 'edited_':
        continue

    print(f"Found {MapFileName} image, will work with it")

    OutputData['cave/bunkeri'].append(MapFileName)


    ############### Getting the picture in 'npy format and precomputing
    ############### isinside, entrances, marked_points

    ############### Verifying if we have a pkl file 

    PklName = MapFileName+".pkl"
    PklFileExists = os.path.isfile("Pickles\\"+PklName)
    if not PklFileExists:
        print("Didn't find a pkl file")
    if PklFileExists:
        toUse = input(f"Found a .pkl file for {MapFileName}. Do you want me to use it? Enter y/n: ")
        PklFileExists = toUse == 'y'
    
    ############### We will create pkl file MapFileName.pkl; if it existed, we will replace it
    place_to_save = {}

    ############### In some cases we will need col_err to compute
    col_err_given = False


    start_time = time.time()


    if PklFileExists:
        with open("Pickles\\"+PklName, 'rb') as file:
            SavedData = pickle.load(file)
        place_to_save = SavedData.copy()

        start_time = time.time()


    ################# Let's get the graphical data

    if FORMAT == 'jpg':
        data = np.array(Image.open(MapFileName+'.jpg'))
    else:
        data = np.array(Image.open(MapFileName+'.png').convert('RGB'))
    shape = data.shape
    place_to_save['data'] = data.copy()
    place_to_save['MapFileName'] = MapFileName





    ################ Find entrances

    if PklFileExists and 'entrances' in SavedData.keys():
        entrances = SavedData['entrances']
    else:
        if not col_err_given:   
            print('Indicate the color error:')
            col_err = int(input('col_err='))
            col_err_given = True

        print('Tell me which color was used to mark the entrances:')

        R = int(input('R='))
        G = int(input('G='))
        B = int(input('B='))

        entrances_color = [R,G,B]

        start_time = time.time()

        entrances = []

        not_counted = np.array( [ [True]*data.shape[1] ]*data.shape[0] )

        for (i,j) in itertools.product(range(shape[0]), range(shape[1])):
            #search for an entrance
            if (dist_infty(data[i,j], entrances_color) <= col_err) and not_counted[i,j] :
                concomp = connected_comp([i,j], data, lambda i,j : dist_infty(data[i,j], entrances_color) <= col_err)
                for v in concomp:
                    not_counted[v[0], v[1]] = False
                entrances.append(center_of_mass(concomp))

        del not_counted

        end_time = time.time()
        print(f"Found {len(entrances)} entrances, spent {round(end_time-start_time,3)} seconds...")
        start_time = end_time

    place_to_save['entrances'] = entrances.copy()



    #Check how many entrances
    if PklFileExists and 'MaxNumOfEntrances' in SavedData.keys():
        MaxNumOfEntrances = SavedData['MaxNumOfEntrances']
    else:
        MaxNumOfEntrances = max(MaxNumOfEntrances, len(entrances))
    
    place_to_save['MaxNumOfEntrances'] = MaxNumOfEntrances



    ################ Compute the scale

    if PklFileExists and 'scale' in SavedData.keys() and 'scale_line' in SavedData.keys():
            scale = SavedData['scale']
            scale_line = SavedData['scale_line']
    else:
        if not col_err_given:   
            print('Indicate the color error:')
            col_err = int(input('col_err='))
            col_err_given = True

        print('Tell me the color of the scale line drawn:')

        R = int(input('R='))
        G = int(input('G='))
        B = int(input('B='))

        scale_color = [R,G,B]

        print('SCALE LINE MUST BE HORIZONTAL!!')

        start_time = time.time()

        scale_line = []

        not_counted = np.array( [ [True]*data.shape[1] ]*data.shape[0] )

        for (i,j) in itertools.product(range(shape[0]), range(shape[1])):
            #collect points on the scale line
            if dist_infty(data[i,j], scale_color) <= col_err : 
                scale_line.append([i,j])
                not_counted[i,j] = False

        del not_counted

        scale = 0
        for (v,w) in itertools.product(scale_line, scale_line):
            scale = max(scale, abs(v[0] - w[0]), abs(v[1] - w[1]))

        scale = 1/scale

        end_time = time.time()
        print(f"Found the scale line, scale is {round(scale,4)}, spent {round(end_time-start_time,3)} seconds...")
        start_time = end_time

    place_to_save['scale'] = scale
    place_to_save['scale_line'] = scale_line.copy()


    ############### Determine isinside

    if PklFileExists and 'isinside' in SavedData.keys():
        isinside = SavedData['isinside']
    else:
        if not col_err_given:   
            print('Indicate the color error:')
            col_err = int(input('col_err='))
            col_err_given = True

        isinside = np.array( [ [False]*data.shape[1] ]*data.shape[0] )

        #Make sure that entrances are marked _inside_ the cave!!
        for v in connected_comp(entrances[0], data, lambda i,j : dist_infty(data[i,j], [255,255,255]) > col_err):
            isinside[v[0], v[1]] = True

        end_time = time.time()
        print(f"Determined which pixels are inside the cave, spent {round(end_time-start_time,3)} seconds...")
        start_time = end_time

    place_to_save['isinside'] = isinside.copy()


    print('Start computing...')


    ############### Find boundary
    if PklFileExists and 'bdry' in SavedData.keys():
        bdry = SavedData['bdry'] 
    else:
        bdry = getbdry(data, isinside)
    place_to_save['bdry'] = bdry.copy()


    ############## Find boundary components

    if PklFileExists and 'bdry' in SavedData.keys() and 'bdry_comps' in SavedData.keys():
        bdry_comps = SavedData['bdry_comps']
    else:
        bdry_comps = []
        not_counted = np.array( [ [True]*data.shape[1] ]*data.shape[0] )

        for (i,j) in itertools.product(range(shape[0]), range(shape[1])):
            if bdry[i,j] and not_counted[i,j] :
                concomp = connected_comp([i,j], data, lambda i,j : bdry[i,j])
                for v in concomp:
                    not_counted[v[0], v[1]] = False
                bdry_comps.append(concomp)

        del not_counted
        end_time = time.time()
        print(f"Determined the boundary of the cave; I found {len(bdry_comps)} boundary components in total, spent {round(end_time-start_time,3)} seconds...")
        start_time = end_time

    place_to_save['bdry_comps'] = bdry_comps.copy()



    ############### Compute area and perimeter

    if PklFileExists and 'area' in SavedData.keys():
        area = SavedData['area']
    else:
        area = round(scale*scale*compute_area(data, isinside),3)
        end_time = time.time()
        print(f"Area is computed, the value is {area}, spent {round(end_time-start_time,3)} seconds...")
        start_time = end_time
    place_to_save['area'] = area

    if (
        PklFileExists 
        and 'per' in SavedData.keys()
        and 'bdry_traj' in SavedData.keys()
        and 'bdry_seeds' in SavedData.keys()
        and 'bdry_sinks' in SavedData.keys()
        and 'bdry_lengths' in SavedData.keys()
    ):
        per = SavedData['per']
        bdry_traj = SavedData['bdry_traj']
        bdry_seeds = SavedData['bdry_seeds']
        bdry_sinks = SavedData['bdry_sinks']
        bdry_lengths = SavedData['bdry_lengths']
    else:
        per = 0
        bdry_traj = []
        bdry_seeds = []
        bdry_sinks = []
        bdry_lengths = []
        for i in range(len(bdry_comps)):
            [l,seed, sink, traj_local] = bdry_comp_length(data, bdry_comps[i])
            bdry_traj.append(traj_local)
            bdry_seeds.append(seed)
            bdry_sinks.append(sink)
            bdry_lengths.append(l)
            per = per + scale*l + scale*dist_E(seed, sink)

        end_time = time.time()
        print(f"Perimeter is computed, the value is {round(per,3)}, spent {round(end_time-start_time,3)} seconds...")
        start_time = end_time
        
    place_to_save['per'] = per
    place_to_save['bdry_traj'] = bdry_traj.copy()
    place_to_save['bdry_seeds'] = bdry_seeds.copy()
    place_to_save['bdry_sinks'] = bdry_sinks.copy()
    place_to_save['bdry_lengths'] = bdry_lengths.copy()
        



    ############### Computing distances

    if (
        PklFileExists
        and 'dist' in SavedData.keys()
        and 'traj' in SavedData.keys()
    ):
        dist = SavedData['dist']
        traj = SavedData['traj']
    else:
        dist = []
        traj = []
        for i in range(len(entrances)):
            [dist1, traj1] = getdist(data, entrances[i], bdry, isinside)
            dist.append(dist1)
            traj.append(traj1)
            end_time = time.time()
            print(f"Distances to Entrance {i} are computed, spent {round(end_time-start_time,3)} seconds...")
            start_time=end_time
    
    place_to_save['dist'] = dist.copy()
    place_to_save['traj'] = traj.copy()

    ################# Find the most remote point
    if (
        PklFileExists
        and 'd' in SavedData.keys()
        and 'v' in SavedData.keys()
    ):
        d = SavedData['d']
        v = SavedData['v']
    else:
        d=0
        v=[]
        for (i,j) in itertools.product(range(data.shape[0]), range(data.shape[1])):
            if isinside[i,j]:
                m = dist[0][i,j]
                for k in range(len(entrances)):
                    m = min(m,dist[k][i,j])
                if d < m:
                    d = m
                    v = [i,j]

        end_time = time.time()
        print(f"The farthest point in the cave is found, the distance is {round(d*scale,3)}, spent {round(end_time-start_time,3)} seconds...")
        start_time=end_time

    place_to_save['d'] = d
    place_to_save['v'] = v

    ################ Find the index of the nearest entrance

    if PklFileExists and 'nearest_entrance' in SavedData.keys():
        nearest_entrance = SavedData['nearest_entrance']
    else:
        nearest_entrance = 0
        for i in range(len(entrances)):
            if dist[i][v[0], v[1]] < dist[nearest_entrance][v[0],v[1]]:
                nearest_entrance = i

    place_to_save['nearest_entrance'] = nearest_entrance


    #draw trajectories
    corners_local = []
    for i in range(len(entrances)):
        point = v
        while traj[i][point[0], point[1]]:
            for j in line(point, traj[i][point[0], point[1]], data):
                data[j[0],j[1]] = [255,0,0]
            point = traj[i][point[0], point[1]]


    end_time = time.time()
    print(f"Trajectory to the farthest point is drawn, spent {round(end_time-start_time,3)} seconds...")
    start_time=end_time


    #highlight boundary
    for i in range(len(bdry_comps)):
        if bdry_lengths[i] > 0:
            point = bdry_sinks[i]
            while bdry_traj[i][point[0], point[1]]:
                for j in line(point, bdry_traj[i][point[0], point[1]], data):
                    data[j[0],j[1]] = [255,0,0]
                point = bdry_traj[i][point[0], point[1]]
    


    #creating file edited_...
    Image.fromarray(data).save('edited_' + MapFileName + '.jpg')
    img = Image.open('edited_' + MapFileName + '.jpg')
    draw = ImageDraw.Draw(img)
    #font = ImageFont.truetype('Pillow/Tests/fonts/FreeMonoBold.ttf', 40)
    font = ImageFont.truetype('arial.ttf', 40)
    font1 = ImageFont.truetype('arial.ttf', 20)

    turning_corners = []
    length_prev = []
    length_next = []
    angles = []

    for i in range(len(entrances)):
        draw.text((entrances[i][1], entrances[i][0]), str(i+1), (102,0,204), font=font)

        turning_corners.append([])
        length_prev.append([])
        length_next.append([])
        angles.append([])
        corners_local[i] = list(reversed(corners_local[i]))
        if len(corners_local[i]) > 2:
            j = 0
            # corner_N = 1
            point0 = corners_local[i][j]
            length_local = []
            while j < len(corners_local[i])-2:
                point1 = corners_local[i][j+1]
                point2 = corners_local[i][j+2]
                edge1 = [point1[0] - point0[0], point1[1] - point0[1]]
                edge2 = [point2[0] - point1[0], point2[1] - point1[1]]
                if angle_btw(edge1,edge2) != 0:
                    # CornerInfo['cave/bunkeri'].append(MapFileName)
                    # CornerInfo['entrance_N'].append(i+1)
                    # CornerInfo['corner_N'].append(corner_N)
                    # CornerInfo['angle'].append(round(angle_btw(edge1,edge2),3))
                    angles[i].append(round(angle_btw(edge1,edge2),3))
                    length_local.append(round(scale*dist_E(point0,point1),3))
                    # draw.text((point1[1], point1[0]), str(round(angle_btw(edge1,edge2),0)), (102,0,204), font=font1)
                    turning_corners[i].append(point1)
                    point0 = point1
                    # corner_N += 1
                j += 1
            length_local.append(round(scale*dist_E(point0,v),3))
            length_prev[i] = length_local[:-1]
            length_next[i] = length_local[1:]
            # CornerInfo['length_previous'] = CornerInfo['length_previous'] + length_local[:-1]
            # CornerInfo['length_next'] = CornerInfo['length_next'] + length_local[1:]


    for i in range(len(entrances)):
        length_local = []
        wind = 0
        corner_N = 1
        M = 0
        N = 0
        for j in range(len(turning_corners[i])):
            wind += angles[i][j]
            M = M + length_prev[i][j]
            if length_next[i][j] >= min_cordist:
                CornerInfo['cave/bunkeri'].append(MapFileName)
                CornerInfo['entrance_N'].append(i+1)
                CornerInfo['corner_N'].append(corner_N)
                CornerInfo['angle'].append(wind)
                if i == nearest_entrance:
                    CornerInfo['nearest_entrance'].append('yes')
                else:
                    CornerInfo['nearest_entrance'].append('no')
                length_local.append(M)
                draw.text((turning_corners[i][j][1], turning_corners[i][j][0]), str(round(wind,0)), (102,0,204), font=font1)
                corner_N += 1
                wind = 0
                M = 0
                N = length_next[i][j]
        length_local.append(N)
        CornerInfo['length_previous'] = CornerInfo['length_previous'] + length_local[:-1]
        CornerInfo['length_next'] = CornerInfo['length_next'] + length_local[1:]


    img.save('edited_' + MapFileName + '.jpg')

    with open('Pickles\\'+MapFileName+'_general.pkl', 'wb') as fpickle:
        pickle.dump(place_to_save, fpickle)

    end_time = time.time()
    print('Cave/bunker '+MapFileName+f' has been measured, spent {round(end_time-start_time0,3)} seconds in total\n')

    OutputData['Area'].append(area)
    OutputData['Perimeter'].append(round(per,3))
    OutputData["distance"].append(round(d*scale,3))



pd.DataFrame(OutputData).to_excel("result.xlsx", index=False)
pd.DataFrame(CornerInfo).to_excel("corners.xlsx", index=False)


print('finished!')



