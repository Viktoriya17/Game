# -*- coding: utf-8 -*-

import multiprocessing as mp
from pygame.locals import *
from random import randint
from time import sleep
from os import system
import pygame as pg
import pandas as pd
import filterlib as flt
import blink as blk
from pyOpenBCI import OpenBCIGanglion


def blinks_detector(quit_program, blink_det, blinks_num, blink,):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)
        #print(smp_flted)

        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:
                connected.set()
                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()
                
                
####################################################
    SYMULACJA_SYGNALU = False
####################################################
    mac_adress = 'e5:32:b4:53:55:ba'
####################################################

    clock = pg.time.Clock()
    frt = flt.FltRealTime()
    brt = blk.BlinkRealTime()

    if SYMULACJA_SYGNALU:
        df = pd.read_csv('dane_do_symulacji/data.csv')
        for sample in df['signal']:
            if quit_program.is_set():
                break
            detect_blinks(sample)
            clock.tick(200)
        print('KONIEC SYGNAŁU')
        quit_program.set()
    else:
        board = OpenBCIGanglion(mac=mac_adress)
        board.start_stream(detect_blinks)

if __name__ == "__main__":


    blink_det = mp.Queue()
    blink = mp.Value('i', 0)
    blinks_num = mp.Value('i', 0)
    connected = mp.Event()
    quit_program = mp.Event()

    proc_blink_det = mp.Process(
        name='proc_',
        target=blinks_detector,
        args=(quit_program, blink_det, blinks_num, blink,)
        )

    # rozpoczęcie podprocesu
    proc_blink_det.start()
    print('subprocess started')

    ############################################
    # Poniżej należy dodać rozwinięcie programu
    ############################################
    # console functions
    def clear_console():
        system("clear")

    # colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    color = (red, green, blue)

    background_color = white

    blue_chance = 20
    green_chance = 20
    red_chance = 60

    def get_random_color():
        rnd = randint(1, 100)
        if (rnd <= blue_chance):
            return color[2]
        elif (rnd > blue_chance and rnd <= blue_chance + green_chance):
            return color[1]
        else:
            return color[0]


    # sizes
    rect_height = 100
    rect_width = 100
    rect_size = (rect_width, rect_height)
    circle_radius = 50

    canvas_height = 600
    canvas_width = 800
    canvas_size = (canvas_width, canvas_height)

    margin = 50
    font_size = 40

    font_y = (margin - font_size) / 2
    font_x = font_size
    font_cords = (font_x, font_y)

    # rectangles positions
    def get_random_rect_pos():
        x = randint(margin, canvas_height - rect_width - margin)
        y = randint(margin, canvas_height - rect_height - margin)
        return (x, y)

    # circles positions
    def get_random_circle_pos():
        x = randint(margin + circle_radius, canvas_height - circle_radius - margin)
        y = randint(margin + circle_radius, canvas_height - circle_radius - margin)
        return (x, y)

    # figure spawn functions
    def spawnRectAtPos(pos, color):
        pg.draw.rect(canvas, color, Rect(pos, rect_size))

    def spawnCircleAtPos(center_pos, color):
        pg.draw.circle(canvas, color, center_pos, circle_radius)

    def clear_canvas():
        rect = Rect(margin, margin, canvas_width - 2 * margin, canvas_height - 2 * margin)
        pg.draw.rect(canvas, background_color, rect)
        pg.display.update()

    # program start

    clear_console()
    print("Mrugaj tylko jak zobaczyć czerwoną kropkę. Do wykorzystania masz 3 życia.")
    input("Press enter to start")

    # pg initialization
    pg.init()
    canvas = pg.display.set_mode(canvas_size)

    # text setup


    pg.font.init()
    font = pg.font.SysFont('Comic Sans MS', font_size)

    clear_canvas()

    # time setup
    time = 0 # time in milliseconds till last figure change
    period_visibility = 500
    period_change = 2000
    delay = 0.01 # 10ms 

    # game variables setup
    reaction = False
    red_cirle = False
    lives = 3
    score = 0

    def display_text():
        clear_text()
        text = "Lives: " + str(lives) + " | " + "Score: " + str(score)
        rendered_text = font.render(text, False, black)
        canvas.blit(rendered_text, font_cords)
        pg.display.update()

    def clear_text():
        rect = Rect(0, 0, canvas_width, margin)
        pg.draw.rect(canvas, background_color, rect)

    canvas.fill(background_color)
    pg.display.update()

    circle_chance = 75
    rect_chance = 25

    while True:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                exit(0)
        pressed_keys = pg.key.get_pressed()
        if pressed_keys[pg.K_SPACE] or blink.value == 1:
            print('BLINK!')
            reaction = True
            blink.value = 0
        sleep(delay)
        time += 10

        if time > period_visibility and time < period_change:
            clear_canvas()
            display_text()
        if time > period_change:
            clear_canvas()
            time = 0
            if red_cirle == True and reaction == True:
                score += 1000
            elif red_cirle == True and reaction == False or red_cirle == False and reaction == True:
                lives -= 1
            display_text()
            reaction = False
            red_cirle = False
            if randint(0, 100) < rect_chance:
                col = get_random_color()
                pos = get_random_rect_pos()
                spawnRectAtPos(pos, col)
            else:
                col = get_random_color()
                pos = get_random_circle_pos()
                if col == red:
                    red_cirle = True
                spawnCircleAtPos(pos, col)
            pg.display.update()
        if lives == 0:
            pg.quit()
            exit(0)



# Zakończenie podprocesów
    proc_blink_det.join()
