# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 17:14:20 2020

@author: AIStars group
"""
from itertools import product

import sys

from graph import Graph
from level_elements import Agent, Box, Goal
from jointaction import ALL_ACTIONS, ActionType, JointAction 

class State:
    MAX_ROW = None
    MAX_COL = None
    goals = []
    colors = []
    walls = []
    
    def __init__(self, copy: 'State', level_lines, goal_state = False):
        
        if copy ==None:
            self.graph = Graph()
            self.agents = []
            self.boxes = []
            self.parent = None
            self.action = JointAction(None)
            self.g = 0
            self.h = -1
            
            State.walls = [[False for _ in range(State.MAX_COL)] for _ in range(State.MAX_ROW)]
            
            #Parse full level (build graph and save mobile entities)
            try:
                for row, line in enumerate(level_lines):
                    for col, char in enumerate(line):
                        if char != '+':
                            cur_node = self.graph.coords2id(col,row,State.MAX_COL)
                            self.graph.add_node(cur_node)
                            for coord in [(-1,0),(1,0),(0,1),(0,-1)]:
                                k = coord[0]
                                l = coord[1]
                                h = min(State.MAX_ROW-1, max(0, row+k))
                                u = min(State.MAX_COL-1, max(0, col+l))
                                if level_lines[h][u]!='+':
                                    dest_node = self.graph.coords2id(h, u, State.MAX_COL)
                                    self.graph.add_node(dest_node)
                                    self.graph.add_edge(cur_node, dest_node, 1) # default distance = 1
                                    #print(str(cur_node) + " ->" + str(dest_node), file=sys.stderr, flush=True)
                            #Parse agents
                            if char in "0123456789":
                                color = State.colors[char]
                                self.agents.append(Agent(char,color,(row, col)))
                            #Parse boxes
                            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                                color = State.colors[char]
                                self.boxes.append(Box(char, color, (row, col)))
                                if goal_state: #Parse goals
                                    print("adding goal to array", file=sys.stderr, flush=True)
                                    State.goals.append(Goal(char,(row, col)))
                            #Parse spaces
                            elif (char ==' '):
                                #Do nothing after creating the node
                                pass
                            else:
                                print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                                sys.exit(1)
                        else:
                            # Walls are not being processed
                            State.walls[row][col] = True
                            pass
                
            except Exception as ex:
                print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
                sys.exit(1)
        else:
            self.agents = copy.agents
            self.boxes = copy.boxes
            self.parent = copy.parent
            self.action = copy.action
            
            self.g = copy.g
            self.h = copy.h

    def get_children(self) -> '[State, ...]':
        '''
        Returns a list of child states attained from applying every applicable action in the current state.
        The order of the actions is random.
        '''
        print('get children', file=sys.stderr, flush=True)
        children = []
        
        all_combinations = list(product(ALL_ACTIONS, repeat=2))
        #for i in n:
        print(str(all_combinations), file=sys.stderr, flush=True)
        #print("length: "+str(len(n)), file=sys.stderr, flush=True)
        for comb in all_combinations:
            for agent_id, action in enumerate(comb):
                #check if combination is valid
                pass
            
        
        for agent in self.agents:
            for action in ALL_ACTIONS:
                # Determine if action is applicable.
                new_agent_coords = agent.coords + (action.agent_dir.d_row, action.agent_dir.d_col)
                
                if action.action_type is ActionType.Move:
                    if self.is_free(new_agent_coords):
                        child = State(self)
                        child.agent_row = new_agent_row
                        child.agent_col = new_agent_col
                        child.parent = self
                        child.action = action
                        child.g += 1
                        children.append(child)
                elif action.action_type is ActionType.Push:
                    if self.box_at(new_agent_row, new_agent_col):
                        new_box_row = new_agent_row + action.box_dir.d_row
                        new_box_col = new_agent_col + action.box_dir.d_col
                        if self.is_free(new_box_row, new_box_col):
                            child = State(self)
                            child.agent_row = new_agent_row
                            child.agent_col = new_agent_col
                            child.boxes[new_box_row][new_box_col] = self.boxes[new_agent_row][new_agent_col]
                            child.boxes[new_agent_row][new_agent_col] = None
                            child.parent = self
                            child.action = action
                            child.g += 1
                            children.append(child)
                elif action.action_type is ActionType.Pull:
                    if self.is_free(new_agent_row, new_agent_col):
                        box_row = self.agent_row + action.box_dir.d_row
                        box_col = self.agent_col + action.box_dir.d_col
                        if self.box_at(box_row, box_col):
                            child = State(self)
                            child.agent_row = new_agent_row
                            child.agent_col = new_agent_col
                            child.boxes[self.agent_row][self.agent_col] = self.boxes[box_row][box_col]
                            child.boxes[box_row][box_col] = None
                            child.parent = self
                            child.action = action
                            child.g += 1
                            children.append(child)
            
        State._RNG.shuffle(children)
        return children
    
    def is_initial_state(self) -> 'bool':
        return self.parent is None
    
    def is_goal_state(self) -> 'bool':
        print(str(State.goals), file=sys.stderr, flush=True)
        print(str(self.boxes), file=sys.stderr, flush=True)
        for goal in State.goals:
            for box in self.boxes:
                
                if(goal.letter == box.letter.lower() and goal.coords == box.coords):
                    print(goal.letter +" = "+ box.letter.lower(), file=sys.stderr, flush=True)
                    print(goal.coords +" = "+  box.coords, file=sys.stderr, flush=True)
                    break
            
            return False    
        return True
    
    def extract_plan(self) -> '[State, ...]':
        plan = []
        state = self
        while not state.is_initial_state():
            plan.append(state)
            state = state.parent
        plan.reverse()
        return plan
    
    def is_free(self, coords: '(row, col)'):
        for agent in self.agents:
            if agent.coord ==coords : return false
            
        for box in self.boxes:
            if box.coord ==coords : return false
        
        if walls[row][col]:return false
        
        return true