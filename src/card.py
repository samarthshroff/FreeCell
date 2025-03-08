from dataclasses import dataclass
# from tkinter import Image, PhotoImage
from color import Color
from src.pile_type import PileType
from suit import Suit
from rank import Rank
from typing import List
import pygame
# from PIL import Image, ImageTk

card_width = 150.0
card_height = 218.0
card_vertical_space = 50.0
layered_card_sprites : pygame.sprite.LayeredUpdates = pygame.sprite.LayeredUpdates()

class Card(pygame.sprite.Sprite):
    image_name = ""
    original_rect: pygame.Rect = pygame.Rect(0.0,0.0,0.0,0.0)
    rect: pygame.Rect = None
    current_pile: PileType = PileType.NONE

    def __init__(self,suit:Suit, rank: Rank):
        pygame.sprite.Sprite.__init__(self)

        self.suit : Suit = suit
        self.rank : Rank = rank
        self.color : Color = Color.BLACK
        if self.suit == Suit.HEARTS or self.suit == Suit.DIAMONDS:
            self.color = Color.RED

        self.children : List[Card] = []
        if self.suit != Suit.ROOT and self.rank != Rank.ROOT:
            self.image_name = f"images/cards/{rank.value}_of_{suit.name.lower()}.png"
            self.image = pygame.image.load(self.image_name).convert()
            self.image = pygame.transform.scale(self.image, (self.image.get_rect().width/3.33,
                                                               self.image.get_rect().height/3.33))

    def set_child_card(self, next_card):
        self.children.append(next_card)

    def update_position(self, top_left_x, top_left_y, add_to_layer:bool = False):
        self.rect = None
        self.original_rect = pygame.Rect(top_left_x, top_left_y, self.image.get_rect().width, self.image.get_rect().height)
        self.rect = pygame.Rect(self.original_rect)
        if add_to_layer:
            layered_card_sprites.add(self)

    def bring_to_front(self):
        layered_card_sprites.change_layer(self, 2)
        layered_card_sprites.move_to_front(self)

    def move_to_back(self):
        layered_card_sprites.change_layer(self, 1)
        #layered_card_sprites.move_to_front(self)

    def reset_layer(self):
        layered_card_sprites.change_layer(self, 1)

    def draw(self, surface: pygame.Surface):

        layered_card_sprites.draw(surface)
        # card_surface = pygame.Surface(self.sprite.image.get_size()).convert_alpha()
        # surface.blit(self.sprite.image, self.sprite.rect)

        # pygame.sprite.LayeredUpdates(self.sprite, layer = 1)
        # self.sprite.layer = 1
        # layered_sprites.change_layer(self.sprite, 1)
        # if(self.is_selected is True):
        #     # self.sprite.layer = 0
        #     layered_sprites.change_layer(self.sprite, 2)
        #     layered_sprites.move_to_front(self.sprite)

        
            #pygame.sprite.LayeredUpdates.move_to_front(self.sprite)

        

        