from dataclasses import dataclass
import pygame
from card import Card


@dataclass
class MoveMetaData:
    selected_card: Card = None
    parent_card: Card = None
    previous_position: pygame.Rect = None
    free_cell_index: int = -1
    home_cell_index: int = -1
