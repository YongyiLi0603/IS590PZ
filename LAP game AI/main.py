import random

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
    used_poi=[]
    peep=choose_map(maps,used_poi) #A set of several coordinates(like [[0,1],[1,1],[1,2]]). peep[0] indicates the 2*2 matrix location and others are points that union
    used_poi.append(peep[0])
