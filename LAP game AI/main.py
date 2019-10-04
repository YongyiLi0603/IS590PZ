import random
import itertools
import copy
import random

test = ['xxxwww','xyyyyw','yyyyyw','zzzzzz','yyyyyw','zzzzzz']
p_maps = [['000000','000000','000000','000000','000000','000000']]

def pruning(m,n,p_maps,direction):
    elements = []
    for i in range(m,m+2):
        for j in range(n,n+2):
            elements.append(test[i][j])
    sub_maps = list(set(list(itertools.permutations(elements,4))))
    tmp_p_maps = []
    flag = True
    for j in range(len(p_maps)):
        tmp = copy.deepcopy(p_maps[j])
        for i in range(len(sub_maps)):
            tmp_ = copy.deepcopy(tmp)
            for l in direction[1:]:
                if sub_maps[i][(l[0]-direction[0][0])*2+(l[1]-direction[0][1])] != tmp_[l[0]][l[1]]:
                    flag = False
                    break
            if flag:
                if len(direction) != 5:
                    for p in range(direction[0][0],direction[0][0]+2):
                        for q in range(direction[0][1],direction[0][1]+2):
                            string = list(tmp_[p])
                            string[q] = sub_maps[i][2*(l[0]-direction[0][0])+l[1]-direction[0][1]]
                            string = "".join(string)
                            tmp_[p] = string
                    tmp_p_maps.append(tmp_)
                else:
                    continue
    p_maps = tmp_p_maps
    
    return p_maps



def random_choose(union_set,used_poi): #sub_fuction of choose_map. union_set is not empty
    for i in union_set:
        if i[0] in used_poi:
            union_set.remove(i)
    l=len(union_set)
    ran=random.randint(0,l-1)
    return union_set[ran]

def choose_map(maps,used_poi): #search all maps(n*n str), return a coordinate(m,n) and a set of union coordinate
    length=len(maps)
    union_1=[]
    union_2=[]
    union_3=[]
    union_4=[]
    for i in range(length-1):
        for j in range(length-1):
            union_count=0
            sol=[[i,j]]
            for x in range(2):
                for y in range(2):
                    if maps[i+x][j+y]!='0':
                        union_count+=1
                        sol.append([i+x,j+y])
            if union_count==1:
                union_1.append(sol)
            if union_count==2:
                union_2.append(sol)
            if union_count==3:
                union_3.append(sol)
            if union_count==4:
                union_4.append(sol)

    if union_2:
        s=random_choose(union_2,used_poi)
    elif union_1:
        s=random_choose(union_1,used_poi)
    elif union_3:
        s=random_choose(union_3,used_poi)
    elif union_4:
        s=random_choose(union_4,used_poi)
    else: s=[]

    return s


if __name__ == "__main__":
    maps=["000000","000xx0","00xxy0","0yyy00","0yy000","000000"]
    p_maps = [['000000','000000','000000','000000','000000','000000']]
    used_poi=[]
    flag = 1
    while 1:
        peep=choose_map(maps,used_poi) #A set of several coordinates(like [[0,1],[1,1],[1,2]]). peep[0] indicates the 2*2 matrix location and others are points that union
        used_poi.append(peep[0])
        p_maps = pruning(peep[0][0],peep[0][1],p_maps,peep)
        if len(p_maps) == 1:
            flag = 0
            for i in p_maps[0]:
                for j in i:
                    if j != '0':
                        flag = 1
                        break
                if flag:
                    break    
        if not flag:
            break
    for i in p_maps:
        print(i)

'''
if __name__ == "__main__":
    maps=["000000","000xx0","00xxy0","0yyy00","0yy000","000000"]
    used_poi=[]
    peep=choose_map(maps,used_poi) #A set of several coordinates(like [[0,1],[1,1],[1,2]]). peep[0] indicates the 2*2 matrix location and others are points that union
    used_poi.append(peep[0])
'''