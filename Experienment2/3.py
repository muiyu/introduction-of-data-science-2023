state = [0, 0, 0, 0]
P = 0
W = 1
S = 2
C = 3

def move(m, n, state):
    if m == n and m == P:
        state[m] = 1 - state[P] 
    else:
        state[m] = 1 - state[m]
        state[n] = 1 - state[n]

def if_valid(state):
    if state[W] == state[S] and state[W] != state[P]:
        return False
    elif state[S] == state[C] and state[S] != state[P]:
        return False
    else:
        return True
    
def if_path_repeat(path):
    if len(path) > 1:
        i = len(path) - 2
        repeat_path = [path[-1]]
        while i > 0:
            if path[i] != path[-1]:
                repeat_path.append(path[i])
                i -= 1
            else:
                break
        
        for _ in repeat_path:
            if _ == path[i]:
                i -= 1
            else:
                return False
        return True


    
def r_c(state, path):
    if state == [1, 1, 1, 1]:
        print(path)
        return
    else:
        new_state_1 = state.copy()
        new_state_2 = state.copy()
        new_state_3 = state.copy()
        new_state_4 = state.copy()

        move(P, W, new_state_1)
        move(P, S, new_state_2)
        move(P, C, new_state_3)
        move(P, P, new_state_4)

        if if_valid(new_state_1) and if_path_repeat(path) == False or len(path) == 1:
            new_path = path.copy()
            new_path.append("P_W")
            r_c(new_state_1, new_path)
        if if_valid(new_state_2) and if_path_repeat(path) == False or len(path) == 1:
            new_path = path.copy()
            new_path.append("P_S")
            r_c(new_state_2, new_path)
        if if_valid(new_state_3) and if_path_repeat(path) == False or len(path) == 1:
            new_path = path.copy()
            new_path.append("P_C")
            r_c(new_state_3, new_path)
        if if_valid(new_state_4) and if_path_repeat(path) == False or len(path) == 1:
            new_path = path.copy()
            new_path.append("P")
            r_c(new_state_4, new_path)
        return
        
import sys
sys.setrecursionlimit(100000)
r_c(state, ["start"])
        