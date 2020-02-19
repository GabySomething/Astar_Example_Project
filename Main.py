import pygame as pg
from Math import *
from Tech import hsv_rgb, TextBox, Button, Click_Handler

window_size = (640, 640)
clock = pg.time.Clock()
display = pg.display
pg.init()
window: pg.Surface = display.set_mode(window_size)
transparency: pg.Surface = pg.Surface(window_size, pg.SRCALPHA, 32).convert_alpha()
FPS = 60
running = True
bkg_color = (220, 220, 230)

grid_size = 16, 16
size = int(window_size[0] / grid_size[0]), int(window_size[1] / grid_size[1])
total_cells = size[0] * size[1]
grid = np.zeros(size, dtype=int)
display.set_caption('A* Testing')
click_handler = Click_Handler()
draw_box = Button('Add Obstacle', 16, (255, 255, 255), (0, 40, 60), rectangle_size=(128, 32))
start_box = Button('Add Start', 16, (255, 255, 255), (0, 60, 0), rectangle_size=(128, 32), position=(128, 0))
goal_box = Button('Add Goal', 16, (255, 255, 255), (60, 0, 0), rectangle_size=(128, 32), position=(256, 0))
clear_box = Button('Clear', 16, (255, 255, 255), (0, 0, 0), rectangle_size=(64, 32), position=(256 + 128, 0))
invert_box = Button('Invert', 16, (0, 255, 0), (0, 40, 20), rectangle_size=(64, 32), position=(256 + 128 + 64, 0))
click_handler.add_object(draw_box, start_box, goal_box, clear_box, invert_box)


# buttons = [draw_box, start_box, goal_box, clear_box]


def to_grid(pos):
    return pos[0] // grid_size[0], pos[1] // grid_size[1]


def mult_by_grid(pos):
    return pos[0] * grid_size[0], pos[1] * grid_size[1]


def gridify(pos):
    return mult_by_grid(to_grid(pos))
    # return (pos[0] // grid_size[0]) * grid_size[0], (pos[1] // grid_size[1]) * grid_size[1]


def change_mode(new_mode):
    global mode
    mode = new_mode


def clear_grid():
    global grid
    grid = np.zeros(size, dtype=int)


def invert_grid():
    global grid
    grid = np.invert(grid)
    grid[start[0]][start[1]] = 0
    grid[end[0]][end[1]] = 0


draw_box.set_click_command(change_mode, 0, 0)
start_box.set_click_command(change_mode, 0, 1)
goal_box.set_click_command(change_mode, 0, 2)
clear_box.set_click_command(clear_grid)
invert_box.set_click_command(invert_grid)
hue = 0
mouse_hover = None
mode = 0
start = (2, 2)
end = (size[0] - 2, size[1] - 2)
path = []
closed_nodes = set()
open_nodes = []
key_press = False
pulse = 0
dist = distance(mult_by_grid(start), mult_by_grid(end)) // 1

while running:
    window.fill(bkg_color)
    transparency.fill((0, 0, 0, 0))
    clock.tick(FPS)
    hue += 1
    pulse += 1
    pulse %= dist + 1
    hue %= 500
    percentage_pulse = pulse / (dist + 1)
    percentage_hue = hue / 500.0
    s_hue = (sin(percentage_hue * 2 * pi) + 1.0) / 2.0
    mouse_pos = pg.mouse.get_pos()
    grid_pos = to_grid(mouse_pos)
    rect_pos = gridify(mouse_pos)

    for event in pg.event.get():
        click_handler.update(event)
        etype = event.type
        if etype == pg.QUIT:
            running = False
            exit()
    if pg.mouse.get_pressed()[0]:
        if not click_handler.mouse_over_object:
            if mode == 0:
                if not (start == grid_pos or end == grid_pos):
                    grid[grid_pos[0]][grid_pos[1]] = 1
            elif mode == 1:
                if not end == grid_pos:
                    start = grid_pos
                    grid[grid_pos[0]][grid_pos[1]] = 0
            elif mode == 2:
                if not start == grid_pos:
                    end = grid_pos
                    grid[grid_pos[0]][grid_pos[1]] = 0
    elif pg.mouse.get_pressed()[2]:
        grid[grid_pos[0]][grid_pos[1]] = 0
    keys = pg.key.get_pressed()
    if keys[pg.K_RETURN] and not key_press:
        key_press = True
        unpack = pathfind(start, end, grid, True)
        if unpack is None:
            path = []
            open_nodes = []
            closed_nodes = []
        else:
            path, open_nodes, closed_nodes = unpack
            dist = len(path) * 16  ##distance(mult_by_grid(start), mult_by_grid(end)) // 1

    elif not keys[pg.K_RETURN]:
        key_press = False
    for n in range(len(closed_nodes)):
        node = closed_nodes[n]
        pg.draw.rect(transparency, (125, 125, 125, (((1 - n / len(closed_nodes) + percentage_pulse) * 1) % 1) * 170),
                     (node[0] * grid_size[0], node[1] * grid_size[1], grid_size[0], grid_size[1]))
    for n in open_nodes:
        node = n[1]
        pg.draw.rect(transparency, (200, 125, 125),
                     (node[0] * grid_size[0], node[1] * grid_size[1], grid_size[0], grid_size[1]))
    pg.draw.rect(window, (0, 255, 0), (start[0] * grid_size[0], start[1] * grid_size[1], grid_size[0], grid_size[1]))
    pg.draw.rect(window, (255, 0, 0), (end[0] * grid_size[0], end[1] * grid_size[1], grid_size[0], grid_size[1]))

    pg.draw.rect(window, hsv_rgb(percentage_hue, 1, 1), (rect_pos[0], rect_pos[1], grid_size[0], grid_size[1]))
    for i in range(len(grid)):
        row = grid[i]
        for j in range(len(row)):
            if row[j]:
                pg.draw.rect(transparency, hsv_rgb(0.1 * (s_hue + (i * j) / total_cells) + 0.4, 1, 0.3),
                             (i * grid_size[0], j * grid_size[1], grid_size[0], grid_size[1]))
    for x in range(0, window_size[0], grid_size[0]):
        pg.draw.line(transparency, (0, 0, 0, 125), (x, 0), (x, window_size[1]))
    for y in range(0, window_size[1], grid_size[1]):
        pg.draw.line(transparency, (0, 0, 0, 125), (0, y), (window_size[0], y))
    for i in range(len(path)):
        if i + 1 >= len(path):
            continue
        closeness = i / (len(path) - 1)
        x1, y1 = path[i]
        point1 = x1 * grid_size[0] + grid_size[0] / 2.0, y1 * grid_size[1] + grid_size[1] / 2.0
        x2, y2 = path[i + 1]
        point2 = x2 * grid_size[0] + grid_size[0] / 2.0, y2 * grid_size[1] + grid_size[1] / 2.0
        pg.draw.line(transparency, (0, 0, 0), point1, point2, 6)
        pg.draw.line(transparency, hsv_rgb((percentage_hue + closeness) % 1, 1, 1), point1, point2, 4)
    click_handler.render_objects(transparency)
    window.blit(transparency, (0, 0))

    display.update()

pg.quit()
