import os
from textwrap import fill
# from tkinter import CENTER, NW, Canvas, Frame, BOTH, Label, PhotoImage, Tk, Widget
# from PIL import Image, ImageTk
from typing import List

import pygame
from card import Card, card_vertical_space,card_width, card_height
from freecell import FreeCell, total_cascade_piles, total_free_cells, total_home_cells

class FreeCellCanvas():
    def __init__(self, free_cell: FreeCell, surface: pygame.Surface):
        super().__init__()
        self.surface = surface     

        self.free_cell_top_x : List[int]= []
        self.free_cell_top_y : List[int]= []

        self.home_cell_top_x : List[int]= []
        self.home_cell_top_y : List[int]= []

        self.cascade_cell_top_x : List[int]= []
        self.cascade_cell_top_y : List[int]= []

        self.free_cell = free_cell
        self.canvas = None
        print("Free cell canvas constructor")
        self.init_ui()

    def init_ui(self):
        for i in range (0,total_free_cells):
            free_cell_x = 10+(10*i)+(i*card_width)
            self.free_cell_top_x.append(free_cell_x)
            self.free_cell_top_y.append(10)
            self.free_cell.update_free_cell_rects(free_cell_x, 10)

            home_cell_x = 800+(10*i)+(i*card_width)
            self.home_cell_top_x.append(home_cell_x)
            self.home_cell_top_y.append(10)
            self.free_cell.update_home_cell_rects(home_cell_x, 10)

        for i in range (0,total_cascade_piles):
            cascade_cell_x = 10+(30*i)+(i*card_width)
            self.cascade_cell_top_x.append(cascade_cell_x)
            self.cascade_cell_top_y.append(275)
            
            if(self.free_cell.cascade_pile_root.children != None):
                card = self.free_cell.cascade_pile_root.children[i]
                self.free_cell.update_cascade_pile_root_rects(self.cascade_cell_top_x[i], self.cascade_cell_top_y[i])
                self.set_card_position(card, self.cascade_cell_top_x[i], self.cascade_cell_top_y[i])

    def set_card_position(self, card: Card, top_x, top_y):
        if(card == None):
            return

        card.update_position(top_x, top_y, True)

        if(card.children != None and len(card.children) == 1):
            self.set_card_position(card.children[0], top_x, top_y+card_vertical_space)

    def draw_ui(self):   
        for i in range(len(self.free_cell_top_x)):
            pygame.draw.rect(self.surface, "black",(self.free_cell_top_x[i], self.free_cell_top_y[i], card_width,card_height), 1)

            pygame.draw.rect(self.surface, "gray",(self.home_cell_top_x[i], self.home_cell_top_y[i], card_width,card_height))
            
        for i in range(len(self.cascade_cell_top_x)):
            pygame.draw.rect(self.surface, "black",(self.cascade_cell_top_x[i], self.cascade_cell_top_y[i], card_width,card_height), 1)
            card = self.free_cell.cascade_pile_root.children[i]
            self.draw_cascade_cards(card)


    def draw_cascade_cards(self, card : Card):        
        if(card == None):
            return
        
        card.draw(self.surface)

        if(card.children != None and len(card.children) == 1):
            self.draw_cascade_cards(card.children[0])
