from PIL import Image
import numpy as np
from math import sqrt, floor, hypot, atan2, pi
from PIL import ImageFont
from PIL import ImageDraw
import itertools
import array







def center_of_mass(points):   #points is a vector containing points on the plane
    N = len(points)
    c = [0,0]
    for v in points:
        c[0] += v[0]
        c[1] += v[1]
    return [floor(c[0]/N), floor(c[1]/N)]


def dist_infty(a,b):
    d = 0
    for i in range(len(a)):
        d = max(d, abs(a[i] - b[i]))
    return d


def dist_E(a,b):
    d = 0
    for i in range(len(a)):
        d += (a[i] - b[i])*(a[i] - b[i])
    return sqrt(d)


def angle_btw(a,b): #returns signed angle in degrees
    A = hypot(a[0], a[1])
    B = hypot(b[0], b[1])
    if A == 0 or B == 0:
        return 0
    prod = a[0]*b[0] + a[1]*b[1]
    det = a[0]*b[1] - a[1]*b[0]
    return (atan2(det, prod)/pi)*180




def graph_neigh(data, isinside, v0, n):
    Neib = [v0]
    lev0 = [v0]
    lev1 = []
    step = 0
    been = np.array( [ [False]*(2*n+1) ]*(2*n+1) )
    been[n,n] = True

    while (step < n) and lev0:
        for v in lev0:
            for s in [[1,0], [0,1], [-1,0], [0,-1], [1,1], [-1,1], [1,-1], [-1,-1]]:
                if ( inrange(data, [v[0]+s[0], v[1]+s[1]]) 
                        and (not been[ v[0]+s[0]-v0[0]+n, v[1]+s[1]-v0[1]+n ]) 
                        and isinside[v[0]+s[0], v[1]+s[1]] ):
                    lev1.append([v[0]+s[0],v[1]+s[1]])
                    been[ v[0]+s[0]-v0[0]+n, v[1]+s[1]-v0[1]+n ] = True
                    Neib.append([v[0]+s[0],v[1]+s[1]])
        lev0 = lev1
        lev1 = []
        step += 1

    return Neib



def find_nearest_inside(data, isinside, v0):
    if isinside[v0[0], v0[1]]:
        return v0
    
    if v0[0] < 0:
        v0[0] = 0
    if v0[0] >= data.shape[0]:
        v0[0] = data.shape[0]-1
    if v0[1] < 0:
        v0[1] = 0
    if v0[1] >= data.shape[1]:
        v0[1] = data.shape[1]-1
    
    inside_not_empty = False
    for (i,j) in itertools.product(range(data.shape[0]), range(data.shape[1])):
        inside_not_empty = isinside[i,j] or inside_not_empty
        
    assert inside_not_empty, "there are no points inside"
    
    lev0 = [v0]
    lev1 = []
    step = 0
    notbeen = np.array( [ [True]*data.shape[1] ]*data.shape[0] )
    notbeen[v0[0],v0[1]] = False

    step = 0

    while True:
        step += 1
        for v in lev0:
            for v1 in ball(v[0], v[1], 1):
                if inrange(data, v1) and isinside[v1[0], v1[1]]:
                    return v1
                if inrange(data, v1) and notbeen[v1[0], v1[1]]:
                    lev1.append(v1)
                    notbeen[v1[0], v1[1]] = False
        lev0 = lev1
        lev1 = []





def compare_lists(a,b):
    res = True
    if len(a) == len(b):
        for i in range(len(a)):
            if a[i] != b[i]:
                res = False
    else:
        res = False
    return res


def connected_comp(v0, data, cond):
    lev0 = [v0]
    lev1 = []
    concomp = [v0]
    been = np.array( [ [False]*data.shape[1] ]*data.shape[0] )
    been[v0[0],v0[1]] = True

    while lev0:
        for v in lev0:
            for s in [[1,0], [0,1], [-1,0], [0,-1], [1,1], [-1,1], [1,-1], [-1,-1]]:
                if inrange(data, [v[0]+s[0], v[1]+s[1]])\
                        and (not been[v[0] + s[0], v[1] + s[1]])\
                        and cond(v[0] + s[0], v[1] + s[1]):
                    lev1.append([v[0] + s[0], v[1] + s[1]])
                    been[v[0] + s[0], v[1] + s[1]] = True
                    concomp.append([v[0] + s[0], v[1] + s[1]])
        lev0 = lev1
        lev1 = []

    return concomp

            


def ball(x,y,r):
    b = []
    for i in range(0,r+1):
        for j in range(0,r+1):
            if i*i + j*j <= r*r:
                b.append([x+i,y+j])
                b.append([x-i,y+j])
                b.append([x+i,y-j])
                b.append([x-i,y-j])

    return b


def line(A,B, data):
    l = []
    d = int(sqrt( (B[0]-A[0])*(B[0]-A[0]) + (B[1]-A[1])*(B[1]-A[1]) ))
    v = [B[0]-A[0], B[1]-A[1]]
    b = ball(0,0,1)
    
    for i in range(d+1):
        p0 = [A[0] + int(i*v[0]/(d+1)), A[1] + int(i*v[1]/(d+1))]
        for p in b:
            if inrange(data, [p0[0] + p[0], p0[1] + p[1]]):
                l.append( [p0[0] + p[0], p0[1] + p[1]] )

    return l




def fat_line(A,B,r, data):
    l = []
    d = int(sqrt( (B[0]-A[0])*(B[0]-A[0]) + (B[1]-A[1])*(B[1]-A[1]) ))
    v = [B[0]-A[0], B[1]-A[1]]
    b = ball(0,0,r)
    
    for i in range(d+1):
        p0 = [A[0] + int(i*v[0]/(d+1)), A[1] + int(i*v[1]/(d+1))]
        for p in b:
            if inrange(data, [p0[0] + p[0], p0[1] + p[1]]):
                l.append( [p0[0] + p[0], p0[1] + p[1]] )

    return l


def inrange(data, v):
    if (v[0] < data.shape[0]) and (v[0] >= 0) and (v[1] < data.shape[1]) and (v[1] >= 0): return True
    else: return False


def compute_area(data, isinside):
    A = 0
    for (i,j) in itertools.product(range(data.shape[0]), range(data.shape[1])):
        if isinside[i,j]: A += 1
    return A


def getdist(data,seed,bdry,isinside):   
    #precompute distances between seed and all v s.t. isinside[v[0],v[1]] = True and fullfill traj array
    #traj must be a np.array whose entries are empty vectors!

    traj = np.empty((data.shape[0], data.shape[1]), dtype = object)
    for i,j in itertools.product(range(data.shape[0]), range(data.shape[1])):
        traj[i,j] = []

    dist = np.array( [ [-0.1]*data.shape[1] ]*data.shape[0] )
    dist[seed[0],seed[1]] = 0

    been = np.array( [ [False]*data.shape[1] ]*data.shape[0] )
    been[seed[0],seed[1]] = True
    lev0 = [seed]
    lev1 = []
    keepforthenext = False

    mdist0, mdist1, Mdist0, Mdist1 = 0,0,0,0

    while lev0:
        mdist1 = mdist0+10
        Mdist1 = Mdist0
        
        for v in lev0:
            for s in [[1,0], [0,1], [-1,0], [0,-1], [1,1], [-1,1], [1,-1], [-1,-1]]:
                if inrange(data, [v[0]+s[0], v[1]+s[1]])\
                        and isinside[v[0]+s[0], v[1]+s[1]]\
                        and (not been[v[0]+s[0], v[1]+s[1]]):
                    if dist[v[0],v[1]] > mdist0+10: keepforthenext= True
                    else:
                        d = dist[v[0],v[1]]+10
                        v0 = []
                        for w in graph_neigh(data, isinside, v, 5):
                            if been[w[0], w[1]]:
                                if (d > dist[w[0],w[1]] + dist_E(w, [v[0]+s[0],v[1]+s[1]]) ):
                                    d = dist[w[0],w[1]] + dist_E(w, [v[0]+s[0],v[1]+s[1]])
                                    v0 = w

                        dist[v[0]+s[0], v[1]+s[1]] = d
                        mdist1 = min(dist[v[0]+s[0], v[1]+s[1]], mdist1)
                        Mdist1 = max(dist[v[0]+s[0], v[1]+s[1]], mdist1)

                        #geodesics look like broken lines between boundary points
                        #(actually, some segments are not straight but go along boundary arcs)
                        #we want to keep track only of boundary points in a trajectory
                        #the rest of the trajectory is reconstructed by drawing lines between consequent pts
                        if traj[v0[0],v0[1]] and (not bdry[v0[0],v0[1]]):
                            traj[v[0]+s[0],v[1]+s[1]] = traj[v0[0],v0[1]]
                        else:
                            traj[v[0]+s[0],v[1]+s[1]].append(v0[0])
                            traj[v[0]+s[0],v[1]+s[1]].append(v0[1])

                        been[v[0]+s[0], v[1]+s[1]] = True
                        lev1.append([v[0]+s[0], v[1]+s[1]])

            if keepforthenext: lev1.append(v)
            keepforthenext = False

        lev0 = lev1
        mdist0 = mdist1
        Mdist0 = Mdist1
        lev1 = []

    return [dist, traj]







#this function takes a boundary component given as a vector of points
#this boundary component must be connected (if we add diagonals)
#and is supposed to approximate a simple curve (3-neighborhood of it)
#the function cuts off a piece of the component, takes a pixel near this piece
#and runs getdist from it
#the largest distance should be approximately the distance of the curve
#the diametr of the boundary component is assumed to be larger than 8
def bdry_comp_length(data, bdry_comp):

    #cut out a small portion of bdry comp aroun a marked point
    isinside = np.array( [ [False]*data.shape[1] ]*data.shape[0] )
    for v in bdry_comp:
        isinside[v[0],v[1]] = True
    isinside0=isinside.copy() #keep a copy for future reason

    v0 = bdry_comp[0]
    for v in graph_neigh(data, isinside, v0, 4):
        isinside[v[0],v[1]] = False

    #there might be several connected comps after cutting. Choose the largest one and delete others
    maxconcomp = []

    for (i,j) in itertools.product(range(data.shape[0]), range(data.shape[1])):
        if isinside[i,j] :
            concomp = connected_comp([i,j], data, lambda a,b: isinside[a,b])
            for v in concomp:
                isinside[v[0], v[1]] = False
            if len(maxconcomp) < len(concomp): maxconcomp = concomp

    for v in maxconcomp:
        isinside[v[0], v[1]] = True
    del maxconcomp


    #now we need a point iside close to v0
    seed = []
    for v in graph_neigh(data, isinside0, v0, 6):
        if isinside[v[0],v[1]]:
            seed = v
            break
    del isinside0

    #it might happen that we have not found any because the component is too small,
    #then we just assume that its length is zero

    if not seed:
        return [0, v0, v0, []]


    #now find the largest distance between seed and other point which isinside

    bdry = getbdry(data, isinside)

    [dist, traj] = getdist(data, seed, bdry, isinside)

    length = 0
    sink = seed
    for (i,j) in itertools.product(range(data.shape[0]), range(data.shape[1])):
        if dist[i,j] > length:
            sink = [i,j]
            length = dist[i,j]

    return [length, seed, sink, traj]









def getbdry(data, isinside):
    bdry = np.array( [ [False]*data.shape[1] ]*data.shape[0] )

    for (i,j) in itertools.product(range(data.shape[0]), range(data.shape[1])):
        if isinside[i,j]:
            for (a,b) in itertools.product(range(-1,2), range(-1,2)):
                if inrange(data, [i+a, j+b]) and not isinside[i+a, j+b]:
                    bdry[i,j] = True

    return bdry




def draw_dist(bats, dist1, dist2, FileOpen, FileSave):

    img = Image.open(FileOpen)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('arial.ttf', 15)

    occupied = np.array( [ [False]*data.shape[1] ]*data.shape[0] )
    cube = []
    for i in range(-13,14):
        for j in range(-46,47):
            cube.append([i,j])

    for v in bats:
        v0 = [v[0]-15,v[1]+5]
        forward = occupied[v0[0], v0[1]]
        if not forward:
            for c in cube:
                occupied[v0[0]+c[0], v0[1]+c[1]] = True

        lim = v[0]+4

        while forward and (v0[0] < lim) and inrange(data, [v0[0]+14,v0[1]]):
            v0 = [v0[0]+1,v0[1]]
            forward = occupied[v0[0], v0[1]]
            if not forward:
                for c in cube:
                    occupied[v0[0]+c[0], v0[1]+c[1]] = True

        lim = v[1]-40

        while forward and (v0[1] > lim) and inrange(data, [v0[0],v0[1]-1]):
            v0 = [v0[0],v0[1]-1]
            forward = occupied[v0[0], v0[1]]
            if not forward:
                for c in cube:
                    occupied[v0[0]+c[0], v0[1]+c[1]] = True

        if forward:
            for c in cube:
                occupied[v0[0]+c[0], v0[1]+c[1]] = True

        draw.text((v0[1],v0[0]), str(min(dist1[v[0],v[1]], dist2[v[0],v[1]])), (0,0,0), font=font)

    img.save(FileSave)




def draw_traj(data, traj, endpoint, filename, color):
    point = endpoint
    while traj[point[0], point[1]]:
        for i in line(point, traj[point[0], point[1]], data):
            data[i[0],i[1]] = color
        point = traj[point[0], point[1]]

    Image.fromarray(data).save(filename)
