# Author: Chunhao Shen, Han Wang

import random

def cut_two_edge(a,b,maps):
    maps[a][b]=0
    maps[b][a]=0

def conn_two_edge(a,b,maps):
    maps[a][b]=1
    maps[b][a]=1

def conn_edge(a,b,maps):
    maps[a][b]=1

def cut_edge(a,b,maps):
    maps[a][b]=0

def init_map(height):
    size=height*(2*height-1)
    maps=[]
    for i in range(size):
        maps_sub=[]
        for j in range(size):
            maps_sub.append(0)
        maps.append(maps_sub)
    #At first all way is through
    for i in range(2*height-1):
        for j in range(height):
            if i == 0:
                if j == 0: continue
                else:
                    conn_two_edge(i*height+j,i*height+j+height,maps)
                    conn_two_edge(i*height+j,i*height+j+height-1,maps)
            elif i ==  2*height-2:
                if j == 0: continue
                else:
                    conn_two_edge(i*height+j,i*height+j-height,maps)
                    conn_two_edge(i*height+j,i*height+j-height-1,maps)
            elif i/2 == 0:
                if j == 0: continue
                else:
                    conn_two_edge(i*height+j,i*height+j-height,maps)
                    conn_two_edge(i*height+j,i*height+j-height-1,maps)
                    conn_two_edge(i*height+j,i*height+j+height,maps)
                    conn_two_edge(i*height+j,i*height+j+height-1,maps)
            else:#i/2!=0
                if j == 0:
                    conn_two_edge(i*height+j,i*height+j+height+1,maps)
                    conn_two_edge(i*height+j,i*height+j-height+1,maps)
                elif j == height-1:
                    conn_two_edge(i*height+j,i*height+j+height,maps)
                    conn_two_edge(i*height+j,i*height+j-height,maps)
                else:
                    conn_two_edge(i*height+j,i*height+j+height,maps)
                    conn_two_edge(i*height+j,i*height+j-height,maps)
                    conn_two_edge(i*height+j,i*height+j+height+1,maps)
                    conn_two_edge(i*height+j,i*height+j-height+1,maps)

    #randomly delete some point
    del_num=1
    for i in range(del_num):
        rani=random.randint(2,(2*height-4))
        if height<=3:
            ranj=2
        else:
            ranj=random.randint(2,height-2)
        #index_del=rani*height+ranj
        if rani/2==0:
            cut_two_edge(rani*height+ranj,rani*height+ranj-height,maps)
            cut_two_edge(rani*height+ranj,rani*height+ranj-height-1,maps)
            cut_two_edge(rani*height+ranj,rani*height+ranj+height,maps)
            cut_two_edge(rani*height+ranj,rani*height+ranj+height-1,maps)
        else:
            cut_two_edge(rani*height+ranj,rani*height+ranj-height,maps)
            cut_two_edge(rani*height+ranj,rani*height+ranj-height+1,maps)
            cut_two_edge(rani*height+ranj,rani*height+ranj+height,maps)
            cut_two_edge(rani*height+ranj,rani*height+ranj+height+1,maps)



    #index 0, 2height, 4height....height(2height-2) is out of the map, randomly choose one to be the start point.
    ran1=random.randint(0,height-1)
    index_start=ran1*2*height
    
    if index_start==0:
        conn_two_edge(0,1,maps)
        conn_two_edge(0,height,maps)
    elif(index_start==height*(2*height-2)):
        conn_two_edge(height*(2*height-2),height*(2*height-3),maps)
        conn_two_edge(height*(2*height-2),height*(2*height-2)+1,maps)

    #We do not have a space for the index finish, we assume only one of the point on the most right can go to the finish point
    #The point on the most right has index 2height-1, 4height-1... height(2height-2)-1
    ran2=random.randint(1,height-1)
    index_finish=ran2*2*height-1
    print(maps)
    return maps, index_start, index_finish


if __name__ == "__main__":
    str_input=input("Please type in the height or width(same) of the puzzle, like 5:")
    height=int(str_input)
    #Initialize n*n points in adjacency matrix which has size (n*n)*(n*n). if (A,B) ==1 then A has a way to B.
    start,finish,maps=init_map(height) 
    