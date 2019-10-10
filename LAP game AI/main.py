import random
import itertools
import copy
import requests
import docopt
from random import choice
import json
from time import sleep

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
            peep=choose_map(maps,used_poi)
            move_instruction = str(peep[0]) #now in form '[0,0]' might require '(0,0)'

        print("\nshhh... sending my matrix", move_instruction)

        submit_move = session.post(url=pz_server_url + "match/{}/move".format(match_id),
                                   json={"move": move_instruction})
        move_result = submit_move.json()["result"]
        print('move_result', move_result)
        print('clue',move_result['outcome'][5:])

        
        if move_result["match_status"] in ["game over", "scored, final"]:
            print('Game over?  Who won?')
            break
        # if move_result['turn_status'] == 'your turn':
        #     print('I will play')

        """Insert a small delay to simulate the "thinking time" of a more challenging game."""
        sleep(3)

    return


if __name__ == "__main__":
    #maps=["000000","000xx0","00xxy0","0yyy00","0yy000","000000"]
    #p_maps = [['000000','000000','000000','000000','000000','000000']]
    used_poi=[]
    maps=[]
    netid = 'chunhao3'
    player_key = '7169e9f9e017'
    pz_server = 'https://jweible.web.illinois.edu/pz-server/games/'
    play_rps(pz_server, netid, player_key)
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