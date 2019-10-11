import random
import itertools
import copy
import requests
import docopt
from random import choice
import json
from time import sleep

used_poi=[]


def pruning(m,n,clue,p_maps,direction):
    elements = []
    #for i in range(m,m+2):
        #for j in range(n,n+2):
            #elements.append(test[i][j])
    for i in len(clue):
        elements.append(clue[i])
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

def play_rps(pz_server_url: str, netid: str, player_key: str):

    # start a fresh session with blank cookies:
    session = requests.Session()
    session.headers = {"Connection": "close"}  # Disables HTTP Keep-Alive

    # query the available game_types to find the RPS id:
    game_search = session.get(url=pz_server_url + "game-types",
                              json={"netid": netid,
                                    "player_key": player_key})

    # TODO: there's not sufficient error checking here...
    try:
        result = game_search.json()['result']
    except Exception as e:
        print('unexpected response:')
        print(game_search.content)
        print('\nfollowed by exception:' + str(e))
        return

    # search for a multi-round, 2-player "Rock, Paper, Scissors":
    game_id = False
    for g in result:
        if (g['category'] == 'Lap' and g['fullname'] == 'Lap 6x6 r4'):
            game_id = g['id']

    if game_id:
        print('Found matching game-type: ', game_id)
    else:
        print('Game not available now.')
        exit()
    game_id = '3'
    # Now request a single match of that game type:
    request_match = session.post(url=pz_server_url + "game-type/{}/request-match".format(game_id),
                                 json={"netid": netid,
                                       "player_key": player_key})

    print('rrrrr', request_match.text)
    match_id = request_match.json()['result']['match_id']

    # This game has multiple "rounds" or "turns".  So loop through a
    # sequence of alternating between requests "await-turn" and "move":

    while True:
        # wait for my turn:
        while True:
            print('\n\nrequesting await-turn now.')
            await_turn = session.get(
                url=pz_server_url + "match/{}/await-turn".format(match_id))
            print(await_turn.text)
            result = await_turn.json()["result"]
            print('Update on previous move(s): ' + json.dumps(result))
            if result["match_status"] == "in play":
                turn_status = result["turn_status"]
                if turn_status == "your turn":
                    # Yea! There was much rejoicing.
                    break  # exit the while loop.
                if "Timed out" in turn_status:
                    print(
                        'PZ-server said it timed out while waiting for my turn to come up...')
                print('waiting for my turn...')
                sleep(3)
                continue
            elif result["match_status"] in ["game over", "scored, final"]:
                print('Game over?  Who won?')
                return
            elif result["match_status"] == "awaiting more player(s)":
                print('match has not started yet. sleeping a bit...')
                sleep(5)
            else:
                raise ValueError('Unexpected match_status: ' + result["match_status"])

        # Ok, now it's my turn...

        # resign the game (for testing purposes)
        # if randint(1, 100) > 99:
        #     print('I am resigning!')
        #     resign = session.post(url=pz_server_url + "match/{}/resign".format(match_id),
        #                           json={})
        #     print(resign.json()["result"])
        #     return

        # submit my move, which is just a uniform random choice:
        # move_instruction = choice(["rock", "paper", "scissors"])
        if result['turn'] in (1,2):
            move_instruction = ['yyyyyy', 'wwwwwy',
                                'wwzxyy', 'wwzxxx', 'zzzxxx', 'zzzzxx']
        else:
            peep=choose_map(p_maps[0],used_poi)
            move_instruction = str(peep[0]) #now in form '[0,0]' might require '(0,0)'

        print("\nshhh... sending my matrix", move_instruction)

        submit_move = session.post(url=pz_server_url + "match/{}/move".format(match_id),
                                   json={"move": move_instruction})
        move_result = submit_move.json()["result"]
        if result['turn'] not in (1,2):
            clue=move_result['outcome'][5:]
            print('move_result', move_result)
            print('clue',move_result['outcome'][5:])
            pruning(peep[0][0],peep[0][1],clue,p_maps,peep)


        if move_result["match_status"] in ["game over", "scored, final"]:
            print('Game over?  Who won?')
            break
        # if move_result['turn_status'] == 'your turn':
        #     print('I will play')

        """Insert a small delay to simulate the "thinking time" of a more challenging game."""
        sleep(3)

    return
def exam(puzzle,x,y,count,dire,region,puzzle_,record):
    direction = [[1,0],[-1,0],[0,-1],[0,1]]
    go = random.randint(0,3)
    if puzzle[x][y] != '0':
        return 0,[[]],puzzle_
    if len(dire[-1]) != 4:
        while go in dire[-1]:
            go = random.randint(0,3)
        dire[-1].append(go)
    else:
        dire[-1].append(go)
    if len(dire[-1]) == 5:
        if len(dire) == 1:
            return count,dire,puzzle_
        else:
            return exam(puzzle,x-direction[dire[-2][-1]][0],y-direction[dire[-2][-1]][1],count,dire[:-1],region,puzzle_,record)
    else:
        if x + direction[go][0] >= len(puzzle) or y + direction[go][1] >= len(puzzle[0]) or x + direction[go][0] < 0 or y + direction[go][1] <0:
            return exam(puzzle,x,y,count,dire,region,puzzle_,record)
        elif puzzle[x+direction[go][0]][y+direction[go][1]] == '0':
            if [x+direction[go][0],y+direction[go][1]] not in record:
                count += 1 
                tmp = list(puzzle_[x + direction[go][0]])
                tmp[y + direction[go][1]] = region
                tmp = "".join(tmp)
                puzzle_[x + direction[go][0]] = tmp
                if go == 0:
                    dire.append([1])
                if go == 1:
                    dire.append([0])
                if go == 2:
                    dire.append([3])
                if go == 3:
                    dire.append([2])
                record.append([x+direction[go][0],y+direction[go][1]])
                return exam(puzzle,x+direction[go][0],y+direction[go][1],count,dire,region,puzzle_,record)
            else:
                return exam(puzzle,x,y,count,dire,region,puzzle_,record)

        else:
            return exam(puzzle,x,y,count,dire,region,puzzle_,record)

def valid(puzzle,x,y,count,dire,region,puzzle_,record):
    direction = [[1,0],[-1,0],[0,-1],[0,1]]
    go = random.randint(0,3)
    if len(dire[-1]) != 4:
        while go in dire[-1]:
            go = random.randint(0,3)
        dire[-1].append(go)
    else:
        dire[-1].append(go)
    if len(dire[-1]) == 5:
        if len(dire) == 1:
            return count,dire,puzzle_
        else:
            return valid(puzzle,x-direction[dire[-2][-1]][0],y-direction[dire[-2][-1]][1],count,dire[:-1],region,puzzle_,record)
    else:
        if x + direction[go][0] >= len(puzzle) or y + direction[go][1] >= len(puzzle[0]) or x + direction[go][0] < 0 or y + direction[go][1] <0:
            return valid(puzzle,x,y,count,dire,region,puzzle_,record)
        elif puzzle[x+direction[go][0]][y+direction[go][1]] == region:
            if [x+direction[go][0],y+direction[go][1]] not in record:
                count += 1 
                tmp = list(puzzle_[x + direction[go][0]])
                tmp[y + direction[go][1]] = region
                tmp = "".join(tmp)
                puzzle_[x + direction[go][0]] = tmp
                if go == 0:
                    dire.append([1])
                if go == 1:
                    dire.append([0])
                if go == 2:
                    dire.append([3])
                if go == 3:
                    dire.append([2])
                record.append([x+direction[go][0],y+direction[go][1]])
                return valid(puzzle,x+direction[go][0],y+direction[go][1],count,dire,region,puzzle_,record)
            else:
                return valid(puzzle,x,y,count,dire,region,puzzle_,record)

        else:
            return valid(puzzle,x,y,count,dire,region,puzzle_,record)
    
    
def generate_(puzzle,x,y,dire,region,count):
    if count != len(puzzle)*len(puzzle[0])/4:
        direction = [[1,0],[-1,0],[0,-1],[0,1]]
        go = random.randint(0,3)
        flag = 0
        if len(dire[-1]) == 4:
            if len(dire) != 1:
                return generate_(puzzle,x-direction[dire[-2][-1]][0],y-direction[dire[-2][-1]][1],dire[:-1],region,count)
            else:
                return puzzle
        while go in dire[-1]:
            go = random.randint(0,3)
        dire[-1].append(go)
        puzzle_ = copy.deepcopy(puzzle)
        if x + direction[go][0] >= len(puzzle) or y + direction[go][1] >= len(puzzle[0]) or x + direction[go][0] < 0 or y + direction[go][1] <0:
            return generate_(puzzle,x,y,dire,region,count)
        elif puzzle[x + direction[go][0]][y + direction[go][1]] != '0':
            return generate_(puzzle,x,y,dire,region,count)
        else:   
            if x + direction[go][0] < len(puzzle) - 1 and y + direction[go][1] < len(puzzle[0]) - 1 and x + direction[go][0] > 0 and y + direction[go][1] > 0:
                if go == 0:
                    if puzzle[x + direction[go][0] + 1][y + direction[go][1]] == '0' and puzzle[x + direction[go][0]][y + direction[go][1]+1] == '0' and puzzle[x + direction[go][0]][y + direction[go][1]-1] == '0':
                        flag = 1
                    else:
                        num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                        num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                        num3,dire3,puzzle_3 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1])
                        index = [i for i, e in enumerate([num1,num2,num3]) if e != 0]
                        way = []
                        num = []
                        for i in index:
                            way.append([puzzle_1,puzzle_2,puzzle_3][i])
                            num.append([num1,num2,num3][i])
                        if 1 in index and 2 in index:
    
                            if sum(num) == len(puzzle)*len(puzzle[0])/4 - count - 1:
                                flag = 1
                                for i in way:
                                    for j in range(len(i)):
                                        puzzle[j] = max(puzzle[j],i[j])
                                count += sum(num)
                            elif min(num) < len(puzzle)*len(puzzle[0])/4 - count - 1 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                tmp = list(puzzle[x + direction[go][0]])
                                tmp[y + direction[go][1]] = region
                                tmp = "".join(tmp)
                                puzzle[x + direction[go][0]] = tmp
                                if num[0] > num[1]:
                                    for i in range(len(way[1])):
                                        puzzle[i] = max(puzzle[i],way[1][i])
                                    count += num[0] +1
                                else:
                                    for i in range(len(way[0])):
                                        puzzle[i] = max(puzzle[i],way[0][i])
                                    count += num[1] + 1
                                return generate_(puzzle,x,y,dire,region,count)
                                
                                
                            elif min(num) % (len(puzzle)*len(puzzle[0])/4) == 0 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                flag = 1
                            else:
                                return generate_(puzzle,x,y,dire,region,count)  
                        else:
                            flag = 1 
                if go == 1:
                    if puzzle[x + direction[go][0] - 1][y + direction[go][1]] == '0' and puzzle[x + direction[go][0]][y + direction[go][1]+1] == '0' and puzzle[x + direction[go][0]][y + direction[go][1]-1] == '0':
                        flag = 1
                    else:
                        num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0] - 1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0] - 1,y + direction[go][1]]) 
                        num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                        num3,dire3,puzzle_3 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1])

                        index = [i for i, e in enumerate([num1,num2,num3]) if e != 0]
                        way = []
                        num = []
            
                        for i in index:
                            way.append([puzzle_1,puzzle_2,puzzle_3][i])
                            num.append([num1,num2,num3][i])
                        if 1 in index and 2 in index:
    
                            if sum(num) == len(puzzle)*len(puzzle[0])/4 - count - 1:
                                flag = 1
                                for i in way:
                                    for j in range(len(i)):
                                        puzzle[j] = max(puzzle[j],i[j])
                                count += sum(num)
                            elif min(num) < len(puzzle)*len(puzzle[0])/4 - count - 1 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                tmp = list(puzzle[x + direction[go][0]])
                                tmp[y + direction[go][1]] = region
                                tmp = "".join(tmp)
                                puzzle[x + direction[go][0]] = tmp
                                if num[0] > num[1]:
                                    for i in range(len(way[1])):
                                        puzzle[i] = max(puzzle[i],way[1][i])
                                    count += num[0] +1
                                else:
                                    for i in range(len(way[0])):
                                        puzzle[i] = max(puzzle[i],way[0][i])
                                    count += num[1] + 1
                                return generate_(puzzle,x,y,dire,region,count)
                                
                                
                            elif min(num) % (len(puzzle)*len(puzzle[0])/4) == 0 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                flag = 1
                            else:
                                return generate_(puzzle,x,y,dire,region,count)
                                
                                
                        else:
                            flag = 1 
                        
                if go == 2:
                    if puzzle[x + direction[go][0] - 1][y + direction[go][1]] == '0' and puzzle[x + direction[go][0]+1][y + direction[go][1]] == '0' and puzzle[x + direction[go][0]][y + direction[go][1]-1] == '0':
                        flag = 1
                    else:
                        num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0] - 1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0] - 1,y + direction[go][1]]) 
                        num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                        num3,dire3,puzzle_3 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1])
                        index = [i for i, e in enumerate([num1,num2,num3]) if e != 0]
                        way = []
                        num = []
            
                        for i in index:
                            way.append([puzzle_1,puzzle_2,puzzle_3][i])
                            num.append([num1,num2,num3][i])
                        if 0 in index and 1 in index:
    
                            if sum(num) == len(puzzle)*len(puzzle[0])/4 - count - 1:
                                flag = 1
                                for i in way:
                                    for j in range(len(i)):
                                        puzzle[j] = max(puzzle[j],i[j])
                                count += sum(num)
                            elif min(num) < len(puzzle)*len(puzzle[0])/4 - count - 1 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                tmp = list(puzzle[x + direction[go][0]])
                                tmp[y + direction[go][1]] = region
                                tmp = "".join(tmp)
                                puzzle[x + direction[go][0]] = tmp
                                if num[0] > num[1]:
                                    for i in range(len(way[1])):
                                        puzzle[i] = max(puzzle[i],way[1][i])
                                    count += num[0] +1
                                else:
                                    for i in range(len(way[0])):
                                        puzzle[i] = max(puzzle[i],way[0][i])
                                    count += num[1] + 1
                                return generate_(puzzle,x,y,dire,region,count)
                                
                                
                            elif min(num) % (len(puzzle)*len(puzzle[0])/4) == 0 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                flag = 1
                            else:
                                return generate_(puzzle,x,y,dire,region,count)
                                
                                
                        else:
                            flag = 1 
                        
                if go == 3:
                    if puzzle[x + direction[go][0] - 1][y + direction[go][1]] == '0' and puzzle[x + direction[go][0]+1][y + direction[go][1]] == '0' and puzzle[x + direction[go][0]][y + direction[go][1]+1] == '0':
                        flag = 1
                    else:
                        num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0] - 1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0] - 1,y + direction[go][1]]) 
                        num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                        num3,dire3,puzzle_3 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1])
                        index = [i for i, e in enumerate([num1,num2,num3]) if e != 0]
                        way = []
                        num = []
            
                        for i in index:
                            way.append([puzzle_1,puzzle_2,puzzle_3][i])
                            num.append([num1,num2,num3][i])
                        if 0 in index and 1 in index:
    
                            if sum(num) == len(puzzle)*len(puzzle[0])/4 - count - 1:
                                flag = 1
                                for i in way:
                                    for j in range(len(i)):
                                        puzzle[j] = max(puzzle[j],i[j])
                                count += sum(num)
                            elif min(num) < len(puzzle)*len(puzzle[0])/4 - count - 1 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                tmp = list(puzzle[x + direction[go][0]])
                                tmp[y + direction[go][1]] = region
                                tmp = "".join(tmp)
                                puzzle[x + direction[go][0]] = tmp
                                if num[0] > num[1]:
                                    for i in range(len(way[1])):
                                        puzzle[i] = max(puzzle[i],way[1][i])
                                    count += num[0] +1
                                else:
                                    for i in range(len(way[0])):
                                        puzzle[i] = max(puzzle[i],way[0][i])
                                    count += num[1] + 1
                                return generate_(puzzle,x,y,dire,region,count)
                                
                                
                            elif min(num) % (len(puzzle)*len(puzzle[0])/4) == 0 and max(num)%(len(puzzle)*len(puzzle[0])/4) == 0:
                                flag = 1
                            else:
                                return generate_(puzzle,x,y,dire,region,count)
                                
                                
                        else:
                            flag = 1 
                        
                if flag:
                    tmp = list(puzzle[x + direction[go][0]])
                    tmp[y + direction[go][1]] = region
                    tmp = "".join(tmp)
                    puzzle[x + direction[go][0]] = tmp
                    dire.append([])
                    return generate_(puzzle,x + direction[go][0],y + direction[go][1],dire,region,count+1)
                    
            else:
                if x + direction[go][0] == 0 or x + direction[go][0] == len(puzzle) -1:
                    if y + direction[go][1] > 0 and y + direction[go][1] < len(puzzle[0]) - 1:
                        if x + direction[go][0] == 0:
                            if go == 1:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1]) 
                            elif go == 2:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                            else:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]])                                    
                        else:
                            if go == 0:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1]) 
                            elif go == 2:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]-1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0]-1,y + direction[go][1]]) 
                            else:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]-1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0]-1,y + direction[go][1]])                                     
                        if 0 in [num1,num2] or go != 1 or go != 0:
                            flag = 1
                        else:
                            if num1 + num2 == len(puzzle)*len(puzzle[0])/4 - count - 1:
                                find = [puzzle_1,puzzle_2]
                                flag = 1
                                for i in find:
                                    for j in range(len(i)):
                                        puzzle[j] = max(puzzle[j],i[j])
                                count += sum([num1,num2])
                            else:
                                if num1%(len(puzzle)*len(puzzle[0])/4) == 0 and num2%(len(puzzle)*len(puzzle[0])/4) == 0:
                                    flag = 1
                                elif max([num1,num2]) < len(puzzle)*len(puzzle[0])/4 and max([num1,num2]) < len(puzzle)*len(puzzle[0])/4 - count - 1:
                                    flag = 0
                                    tmp = list(puzzle[x + direction[go][0]])
                                    tmp[y + direction[go][1]] = region
                                    tmp = "".join(tmp)
                                    puzzle[x + direction[go][0]] = tmp
                                    find = [[num1,puzzle_1],[num2,puzzle_2]]
                                    for i in find:
                                        if i[0] > 0 and i[0] < len(puzzle)*len(puzzle[0])/4:
                                            for j in range(len(i[1])):
                                                puzzle[j] = max(puzzle[j],i[1][j])
                                                flag = 1
                                        if flag:
                                            count += i[0]+1
                                            break
                                    flag = 0
                                    return generate_(puzzle,x,y,dire,region,count)
                                elif max([num1,num2])%(len(puzzle)*len(puzzle[0])/4) == 0 and min([num1,num2]) < len(puzzle)*len(puzzle[0])/4 - count - 1: 
                                    flag = 0
                                    tmp = list(puzzle[x + direction[go][0]])
                                    tmp[y + direction[go][1]] = region
                                    tmp = "".join(tmp)
                                    puzzle[x + direction[go][0]] = tmp
                                    find = [[num1,puzzle_1],[num2,puzzle_2]]
                                    for i in find:
                                        if i[0] > 0 and i[0] < len(puzzle)*len(puzzle[0])/4:
                                            for j in range(len(i[1])):
                                                puzzle[j] = max(puzzle[j],i[1][j])
                                            count += i[0] + 1
                                    return generate_(puzzle,x,y,dire,region,count)
                                else:
                                    return generate_(puzzle,x,y,dire,region,count)
                    else:
                        flag = 1
                            
                if y + direction[go][1] == 0 or y + direction[go][1] == len(puzzle[0])-1:
                    if x + direction[go][0] > 0 and x + direction[go][0] < len(puzzle) - 1:
                        if y + direction[go][1] == 0:
                            if go == 2:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]-1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0]-1,y + direction[go][1]]) 
                            elif go == 0:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                            else:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0],y + direction[go][1]+1,1,[[2]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]+1]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]-1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0]-1,y + direction[go][1]])                                  
                        else:
                            if go == 3:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0]-1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0]-1,y + direction[go][1]]) 
                            elif go == 0:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0]+1,y + direction[go][1],1,[[1]],region,copy.deepcopy(puzzle_),[x + direction[go][0]+1,y + direction[go][1]]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1]) 
                            else:
                                num1,dire1,puzzle_1 = exam(puzzle,x + direction[go][0]-1,y + direction[go][1],1,[[0]],region,copy.deepcopy(puzzle_),[x + direction[go][0]-1,y + direction[go][1]]) 
                                num2,dire2,puzzle_2 = exam(puzzle,x + direction[go][0],y + direction[go][1]-1,1,[[3]],region,copy.deepcopy(puzzle_),[x + direction[go][0],y + direction[go][1]-1])   
                        if 0 in [num1,num2] or go != 2 or go != 3:
                            flag = 1
                        else:
                            if num1 + num2 == len(puzzle)*len(puzzle[0])/4 - count - 1:
                                find = [puzzle_1,puzzle_2]
                                flag = 1
                                for i in find:
                                    for j in range(len(i)):
                                        puzzle[j] = max(puzzle[j],i[j])
                                count += sum([num1,num2])

                            else:
                                if num1%(len(puzzle)*len(puzzle[0])/4) == 0 and num2%(len(puzzle)*len(puzzle[0])/4) == 0:
                                    flag = 1
                                elif max([num1,num2]) < len(puzzle)*len(puzzle[0])/4 and max([num1,num2]) < len(puzzle)*len(puzzle[0])/4 - count - 1:
                                    flag = 0
                                    tmp = list(puzzle[x + direction[go][0]])
                                    tmp[y + direction[go][1]] = region
                                    tmp = "".join(tmp)
                                    puzzle[x + direction[go][0]] = tmp
                                    find = [[num1,puzzle_1],[num2,puzzle_2]]
                                    for i in find:
                                        if i[0] > 0 and i[0] < len(puzzle)*len(puzzle[0])/4:
                                            for j in range(len(i[1])):
                                                puzzle[j] = max(puzzle[j],i[1][j])
                                            flag  =1
                                        if flag:
                                            count += i[0]+1
                                            break
                                    flag = 0
                                    return generate_(puzzle,x,y,dire,region,count)
                                elif max([num1,num2])%(len(puzzle)*len(puzzle[0])/4) == 0 and min([num1,num2]) < len(puzzle)*len(puzzle[0])/4 - count - 1: 
                                    flag = 0
                                    tmp = list(puzzle[x + direction[go][0]])
                                    tmp[y + direction[go][1]] = region
                                    tmp = "".join(tmp)
                                    puzzle[x + direction[go][0]] = tmp
                                    find = [[num1,puzzle_1],[num2,puzzle_2]]
                                    for i in find:
                                        if i[0] > 0 and i[0] < len(puzzle)*len(puzzle[0])/4:
                                            for j in range(len(i[1])):
                                                puzzle[j] = max(puzzle[j],i[1][j])
                                            count += i[0] + 1
                                    return generate_(puzzle,x,y,dire,region,count)
                                else:
                                    return generate_(puzzle,x,y,dire,region,count)
                    else:
                        flag = 1
                if flag:
                    tmp = list(puzzle[x + direction[go][0]])
                    tmp[y + direction[go][1]] = region
                    tmp = "".join(tmp)
                    puzzle[x + direction[go][0]] = tmp
                    dire.append([])
                    return generate_(puzzle,x + direction[go][0],y + direction[go][1],dire,region,count+1)
                else:
                    return generate_(puzzle,x,y,dire,region,count)
    else:
        return puzzle
def get_map(l,w,num):
    puzzle = puzzle = ["".join(['0' for i in range(w)]) for i in range(l)]
    
    x = random.randint(0,len(puzzle)-1)
    y = random.randint(0,len(puzzle[0])-1)
    symbol = []
    for i in range(1,num+1):
        symbol.append(str(i))
    tmp = list(puzzle[x])
    tmp[y] = symbol[0]
    tmp = "".join(tmp)
    puzzle[x] = tmp
    puzzle = generate_(puzzle,x,y,[[]],symbol[0],1)
    flag_ = 0
    while 1:
        for i in symbol[1:]:
            flag = 0
            for m in range(len(puzzle)):
                for n in range(len(puzzle[0])):
                    if puzzle[m][n] == '0':
                        x = m
                        y = n
                        flag = 1
                        break
                if flag:
                    break
            flag = 0
            tmp = list(puzzle[x])
            tmp[y] = i
            tmp = "".join(tmp)
            puzzle[x] = tmp
            puzzle = generate_(puzzle,x,y,[[]],i,1)
            for m in range(len(puzzle)):
                for n in range(len(puzzle[0])):
                    if puzzle[m][n] == i:
                        x = m
                        y = n
                        flag = 1
                        break
                if flag:
                    break
            if valid(puzzle,x,y,1,[[]],i,copy.deepcopy(puzzle),[[x,y]])[0] == len(puzzle)*len(puzzle[0]) / len(symbol):
                flag_ += 1
            else:

                break
        if flag_ == len(symbol) -1:
            break
        else:
            puzzle = ["".join(['0' for i in range(w)]) for i in range(l)]
            x = random.randint(0,len(puzzle)-1)
            y = random.randint(0,len(puzzle[0])-1)
            symbol = []
            for i in range(1,num+1):
                symbol.append(str(i))
            tmp = list(puzzle[x])
            tmp[y] = symbol[0]
            tmp = "".join(tmp)
            puzzle[x] = tmp
            puzzle = generate_(puzzle,x,y,[[]],symbol[0],1)
            flag_ = 0
    return puzzle

if __name__ == "__main__":
    maps=get_map(6,6,4)
    #p_maps = [['000000','000000','000000','000000','000000','000000']]
    p_maps = [['000000','000000','000000','000000','000000','000000']]
    netid = 'yongyi2'
    player_key = 'b92896e0c1a4'
    pz_server = 'https://jweible.web.illinois.edu/pz-server/games/'
    play_rps(pz_server, netid, player_key)
    '''
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

'''
if __name__ == "__main__":
    maps=["000000","000xx0","00xxy0","0yyy00","0yy000","000000"]
    used_poi=[]
    peep=choose_map(maps,used_poi) #A set of several coordinates(like [[0,1],[1,1],[1,2]]). peep[0] indicates the 2*2 matrix location and others are points that union
    used_poi.append(peep[0])
'''
