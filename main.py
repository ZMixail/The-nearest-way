from os.path import abspath
from collections import deque
from random import choice
import pygame as pg

class Robot():
    def __init__(self, type='circle', pos=0):
        self.type = type
        self.pos = pos

    def move(self):
        self.pos = way[way.index(self.pos)-1]

    def draw(self):
        coords = get_coords(self.pos)
        if self.type == 'rect':
            draw_rect(robot_color, coords)
        else:
            draw_circle(robot_color, coords)

class Field():
    def __init__(self, width, height, goal_type):
        self.width = width
        self.height = height
        self.goal_type = goal_type
        self.colors = [field_color for i in range(cell_num)]
        self.free = set()
        self.barriers = set()
        self.passed = set()
        self.stack = []
        self.goal = 0
        self.goal_coords = 0

    def generate_grid(self):
        field.clear(field.passed)
        field.clear(field.barriers)
        i = 0
        while i < cell_num:
            self.free.add(i)
            if i % self.width == self.width - 1:
                i += self.width + 1
            else:
                i += 2
        self.barriers = set([i for i in range(cell_num)])
        self.barriers.difference_update(self.free)
        for i in self.barriers:
            self.colors[i] = bar_color

    def generate_barriers(self, start=0):
        through_line = self.width * 2
        neigh = {start - through_line, start + through_line,
                 start - 2, start + 2}
        neigh.intersection_update(self.free)
        if neigh:
            move = choice(list(neigh))
            dif = (move - start)//2
            if abs(dif) == 1:
                through = start + dif
            elif dif > 0:
                through = move - self.width
            else:
                through = move + self.width
            field.free.discard(start)
            field.barriers.discard(through)
            field.passed.add(start)
            field.passed.add(through)
            field.colors[start] = passed_color
            field.colors[through] = passed_color
            self.stack.append(move)
        else:
            field.free.discard(start)
            field.passed.add(start)
            field.colors[start] = passed_color
            move = self.stack.pop(-1)
        return move

    def clear(self, set):
        for i in set:
            field.colors[i] = field_color
        set.clear()

    def draw(self):
        if self.goal != robot.pos:
            if self.goal_type == 'rect':
                draw_rect(goal_color, self.goal_coords)
            else:
                draw_circle(goal_color, self.goal_coords)
        for this_cell in range(cell_num):
            if this_cell != self.goal:
                color = self.colors[this_cell]
                coords = get_coords(this_cell)
                draw_rect(color, coords)

    def save_maze(self):
        global img_num, sol_num
        file = open('img_num.txt', mode='r')
        img_num = int(file.read())
        file.close()
        sol_num = 0
        path = abspath(f'./images/img{img_num}.png')
        pg.image.save(screen, path)
        file = open('img_num.txt', mode='w')
        file.write(str(img_num+1))
        file.close()

    def save_sol(self):
        global sol_num
        path = abspath(f'./images/sol{img_num}_{sol_num}.png')
        pg.image.save(screen, path)
        sol_num += 1


def graph_from_rectangle(diagonal=False):
    node_num = cell_num
    graph = [set() for i in range(node_num)]
    for index in range(node_num):
        i = index // num_x # Y-axis
        j = index % num_x # X-axis
        neigh = {'top': index-num_x,
                 'down': index+num_x,
                 'left': index-1,
                 'right': index+1}
        diagonals = {'top left': neigh['top']-1,
                     'top right': neigh['top']+1,
                     'down left': neigh['down']-1,
                     'down right': neigh['down']+1}
        if diagonal:
            if i != 0 and j != 0:
                graph[index].add(diagonals['top left'])
            if i != 0 and j != wall_x:
                graph[index].add(diagonals['top right'])
            if i != wall_y and j != 0:
                graph[index].add(diagonals['down left'])
            if i != wall_y and j != wall_x:
                graph[index].add(diagonals['down right'])
        if i != 0:
            graph[index].add(neigh['top'])
        if i != wall_y:
            graph[index].add(neigh['down'])
        if j != 0:
            graph[index].add(neigh['left'])
        if j != wall_x:
            graph[index].add(neigh['right'])
        # Remove barriers from possible moves
        graph[index].difference_update(field.barriers)
    return graph

def dijkstra(start):
    inf = cell_num
    dist = [inf for i in range(cell_num)]
    dist[start] = 0
    queue = deque([start])
    while queue:
        i = queue.popleft()
        for neigh in graph[i]:
            new_dist = dist[i] + 1
            if dist[neigh] > new_dist:
                dist[neigh] = new_dist
                queue.append(neigh)
    return dist

def the_nearest_way(start, finish):
    pos = finish
    way = [pos]
    while dist[pos] != 0:
        for neigh in graph[pos]:
            if dist[pos] - dist[neigh] == 1:
                pos = neigh
                way.append(pos)
                break
    return way

def get_coords(num):
    return (num%num_x * cell,
            num//num_x * cell)

def get_cell_num(coords):
    return (coords[1]//cell)*num_x + coords[0]//cell

def draw_rect(color, coords):
    x = coords[0]
    y = coords[1]
    pg.draw.rect(screen, color, (x, y, cell, cell))

def draw_circle(color, coords):
    x = coords[0] + half
    y = coords[1] + half
    pg.draw.circle(screen, color, (x, y), half)


black     = (0, 0, 0)
white     = (255, 255, 255)
red       = (254, 26, 26)
green     = (0, 255, 0)
blue      = (15, 82, 186)
yellow    = (255, 216, 0)
purple    = (255, 30, 100)

robot_color = green
field_color = white
goal_color = yellow
bar_color = black
passed_color = purple

cell = 100
half = cell // 2
num_x = 11
num_y = 9
wall_x = num_x - 1
wall_y = num_y - 1
cell_num = num_x * num_y

field = Field(width=num_x, height=num_y, goal_type='rect')
robot = Robot(type='rect')

to_generate_maze = input('Do you want to generate maze? (y/n): ')
if to_generate_maze == 'y':
    field.generate_grid()
    gen_pos = 0
    generating_barriers = True
else:
    generating_barriers = False

creating_barriers = not generating_barriers
choosing_goal = False
moving = False
save_img = False
save_sol = False

pg.init()
screen = pg.display.set_mode((num_x*cell, num_y*cell))
pg.display.set_caption('The way')

run = True
while run:
    mouse = pg.mouse.get_pos()
    this_cell = get_cell_num(mouse)
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False
        elif e.type == pg.MOUSEBUTTONDOWN:
            if creating_barriers:
                if this_cell in field.barriers:
                    field.barriers.remove(this_cell)
                    field.colors[this_cell] = field_color
                elif this_cell != field.goal:
                    field.passed.discard(this_cell)
                    field.barriers.add(this_cell)
                    field.colors[this_cell] = bar_color
            elif (choosing_goal and this_cell not in field.barriers
                                and this_cell != robot.pos):
                if goal_color in field.colors:
                    pre_cell = field.colors.index(goal_color)
                    field.colors[pre_cell] = field_color
                field.goal = this_cell
                field.goal_coords = get_coords(this_cell)
                field.colors[this_cell] = goal_color
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_RETURN:
                if creating_barriers:
                    creating_barriers = False
                    choosing_goal = True
                    save_img = True
                    field.clear(field.passed)
                elif choosing_goal:
                    choosing_goal = False
                    moving = True
                    field.clear(field.passed)
                    graph = graph_from_rectangle()
                    dist = dijkstra(start=robot.pos)
                    way = the_nearest_way(start=robot.pos,
                                          finish=field.goal)
            elif e.key == pg.K_BACKSPACE and choosing_goal:
                choosing_goal = False
                field.clear(field.barriers)
                field.clear(field.passed)
                if to_generate_maze == 'y':
                    generating_barriers = True
                    robot.pos = 0
                    field.goal = 0
                    field.generate_grid()
                else:
                    creating_barriers = True
    screen.fill(field_color)
    if generating_barriers:
        if field.free != set():
            gen_pos = field.generate_barriers(gen_pos)
        else:
            generating_barriers = False
            creating_barriers = True
            save_img = True
            field.clear(field.passed)
    elif moving:
        field.passed.add(robot.pos)
        field.colors[robot.pos] = passed_color
        robot.move()
        if robot.pos == field.goal:
            moving = False
            creating_barriers = True
            save_sol = True
    field.draw()
    robot.draw()
    pg.display.update()
    if save_img:
        field.save_maze()
        save_img = False
    elif save_sol:
        field.save_sol()
        save_sol = False
pg.quit()
