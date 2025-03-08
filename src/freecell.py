from typing import List

import pygame
from card import Card, card_vertical_space, layered_card_sprites, card_width, card_height
from color import Color
from rank import Rank
from src.move_meta_data import MoveMetaData
from suit import Suit
# from tkinter import Canvas, Event
import random

total_cascade_piles = 8
total_free_cells = 4
total_home_cells = 4
total_previous_moves : int = 5

class FreeCell:
    deck: List[Card] = []
    home_cells: List[List[Card]] = []
    free_cells: List[Card] = []

    cascade_pile_root_rects: List[pygame.Rect] = []
    home_cell_rects: List[pygame.Rect] = []
    free_cell_rects: List[pygame.Rect] = []
    
    cascade_pile_root: Card
    selected_card : Card = None
    parent_card : Card = None

    # Offset of the trailing cards when a bunch of cards are selected with mouse.
    offset_x : List[int] = []
    offset_y : List[int] = []

    previous_moves_stack : [MoveMetaData] = []

    def __init__(self):
        for suit in Suit:
            if suit == Suit.ROOT:
                continue
            for rank in Rank:
                if rank == Rank.ROOT:
                    continue
                self.deck.append(Card(suit, rank))

    def update_home_cell_rects(self, x, y):
        rect: pygame.Rect = pygame.Rect(x,y,card_width, card_height)
        self.home_cell_rects.append(rect)

    def update_free_cell_rects(self, x, y):
        rect: pygame.Rect = pygame.Rect(x,y,card_width, card_height)
        self.free_cell_rects.append(rect)        

    def update_cascade_pile_root_rects(self, x, y):
        rect: pygame.Rect = pygame.Rect(x,y,card_width, card_height)
        self.cascade_pile_root_rects.append(rect)

    def deal_new_game(self):
        random.shuffle(self.deck)
        self.home_cells.clear()
        self.free_cells.clear()
        self.free_cells = [None] * 4
        self.home_cells = [[]] * 4

        self.cascade_pile_root = Card(Suit.ROOT, Rank.ROOT)
        
        for i in range(0,total_cascade_piles):
            self.cascade_cards(self.cascade_pile_root,i)

    def cascade_cards(self, current_card_node : Card, index):
        if index < 52 and current_card_node is not None:
            next_card = self.deck[index]
            current_card_node.set_child_card(next_card)
            index += total_cascade_piles
            self.cascade_cards(next_card,index)
        else:
            return
        
    def on_input(self, event : pygame.event.Event):
        # # don't take inputs if the game is not active to avoid errors and crashes.
        # if(self.is_game_active is False):
        #     return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            print(f"pos is {pos}")
            cards = self.get_picked_card(pos)
            if cards == None:
                # if there is not collision with the cascade pile then check the free cells 
                # if no collision with the cards from free cell then check with the top card from the home cells.
                # by the way none of this detection will require us to check ONLY with the ONE TOP card and not all the cards behind it (in case of home cells)
                # one way to avoid unnecessary checks is to first check if the pos.y is above the rect.bottom of home and free cell(s) (one cell from each deck should be fine)
                # else return
                # Check if it collides with the free cell
                fc_rect: pygame.Rect = None
                index: int = 0
                for index in range(len(self.free_cell_rects)):
                    if self.free_cell_rects[index].collidepoint(pos[0], pos[1]):
                        fc_rect = self.free_cell_rects[index]
                        break

                if fc_rect != None:
                    self.selected_card = self.free_cells[index]
                    self.parent_card = None
                    self.free_cells[index] = None
            else:
                self.selected_card = cards[0]
                self.parent_card = cards[1]

            self.update_card_offset_with_mouse_pos(pos)
            self.bring_selected_card_trail_to_front()
            print(f"selected card {self.selected_card.suit}:{self.selected_card.rank}")
        
        if event.type==pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            self.move_cards_with_mouse(pos)

        if event.type==pygame.MOUSEBUTTONUP and event.button == 1 and self.selected_card != None:
            self.on_mouse_button_up()

    def on_mouse_button_up(self):
        pos = pygame.mouse.get_pos()
        # Check if collision is with a leaf node card from cascade pile.
        # if no then snap back to original position
        new_parent_card = self.get_possible_new_parent()
        if new_parent_card == None:
            # Check if the card is to be placed in an empty cascade pile area.
            rect: pygame.Rect = None  # pygame.Rect(0.0,0.0,0.0,0.0)
            index: int = 0
            for index in range(len(self.cascade_pile_root_rects)):
                if pygame.Rect.colliderect(self.cascade_pile_root_rects[index], self.selected_card.rect): #self.cascade_pile_root_rects[index].collidepoint(pos[0], pos[1]):
                    rect = self.cascade_pile_root_rects[index]
                    break

            # placing in a cascade pile
            if rect != None:
                # If user wishes to place a card or trail of cards on an empty cascade pile slot.
                if self.cascade_pile_root.children[index] == None and self.is_supermove_legit(index, True):
                    self.cascade_pile_root.children[index] = self.selected_card
                    if self.parent_card != None:
                        self.parent_card.children.remove(self.selected_card)
                else:
                    self.snap_pile_to_original_position()
            # placing in either home or free cell
            else:
                # there should only be one card for placing it in either home or free cell
                if self.selected_card.children == None or len(self.selected_card.children) == 0:
                    # Check if it collides with the free cell
                    fc_rect: pygame.Rect = None
                    for index in range(len(self.free_cell_rects)):
                        if pygame.Rect.colliderect(self.free_cell_rects[index], self.selected_card.rect): #self.free_cell_rects[index].collidepoint(pos[0], pos[1]):
                            fc_rect = self.free_cell_rects[index]
                            break

                    if fc_rect != None:
                        if self.free_cells[index] == None:
                            if self.parent_card != None:
                                self.parent_card.children.remove(self.selected_card)
                            self.free_cells[index] = self.selected_card
                            self.snap_selected_card_to_pos(self.free_cell_rects[index])
                    # if no free cell collides then check for home cells
                    else:
                        hc_rect: pygame.Rect = None
                        for index in range(len(self.home_cell_rects)):
                            if pygame.Rect.colliderect(self.home_cell_rects[index], self.selected_card.rect): #self.home_cell_rects[index].collidepoint(pos[0], pos[1]):
                                hc_rect = self.home_cell_rects[index]
                                break

                        if hc_rect != None:
                            # If the home cell is empty then the selected card MUST be ACE.
                            if len(self.home_cells[index]) == 0 and self.selected_card.rank == Rank.ACE:
                                if self.parent_card != None:
                                    self.parent_card.children.remove(self.selected_card)
                                self.home_cells[index].append(self.selected_card)
                                self.snap_selected_card_to_pos(self.home_cell_rects[index])
                            # ELSE check the top most card placed on this home cell.
                            elif len(self.home_cells[index]) != 0:
                                topmost_card: Card = self.home_cells[index][-1]

                                # it should be of same rank as the selected card
                                # it's rank should be one less than the selected card
                                if (topmost_card.rank == self.selected_card.rank - 1 and
                                        topmost_card.suit == self.selected_card.suit):
                                    if self.parent_card != None:
                                        self.parent_card.children.remove(self.selected_card)
                                    self.home_cells[index].append(self.selected_card)

                # more than one card selected to be placed onto a free or home cell.
                # this is not allowed. snap back to original position.
                else:
                    print(f"card not colliding with any rect. snapping to original position.")
                    self.snap_pile_to_original_position()

        else:
            # check if it is of one rank less and of different suit
            # Yes then check if total cards in pile is only one more than the total of empty free cells
            # Yes then move is legit snap to new location. Call card.update_position
            # else snap to original location.

            is_moved: bool = False

            if self.is_rank_legit(new_parent_card.rank, self.selected_card.rank):
                if self.is_suit_legit(new_parent_card.color, self.selected_card.color):
                    destination_cascade_pile: Card = self.get_vertical_pile_root(self.selected_card.rect.x)
                    if self.is_supermove_legit(destination_cascade_pile, False):
                        new_pos: pygame.Rect = pygame.Rect(new_parent_card.rect)
                        self.snap_pile_to_pos(new_pos)
                        if self.parent_card != None:
                            self.parent_card.children.remove(self.selected_card)
                        is_moved = True
                        if len(new_parent_card.children) == 0:
                            new_parent_card.children.append(self.selected_card)
                        else:
                            new_parent_card.children[0] = self.selected_card

            if is_moved is False:
                self.snap_pile_to_original_position()
        self.move_selected_card_trail_to_back()
        self.selected_card = None
        self.parent_card = None

    def is_rank_legit(self, parent_card_rank: Rank, child_card_rank: Rank) -> bool:
        #if(child_card.rank == Rank.KING and parent_card.rank == ROOT)
        return child_card_rank == parent_card_rank - 1
    
    def is_suit_legit(self, parent_card_color : Color, child_card_color: Color) -> bool:
        return parent_card_color != child_card_color

    def move_selected_card_trail_to_back(self):
        card : Card = self.selected_card

        while(True):
            if(card == None):
                break
            card.move_to_back()
            card = card.children[0] if len(card.children) > 0 else None

    def bring_selected_card_trail_to_front(self):
        card : Card = self.selected_card

        while(True):
            if(card == None):
                break
            card.bring_to_front()
            card = card.children[0] if len(card.children) > 0 else None

    def update_card_offset_with_mouse_pos(self, pos):
        self.offset_x.clear()
        self.offset_y.clear()

        card : Card = self.selected_card

        while(True):
            if(card == None):
                break
            self.offset_x.append(card.rect.left - pos[0])
            self.offset_y.append(card.rect.top - pos[1])
            card = card.children[0] if len(card.children) > 0 else None        

    def move_cards_with_mouse(self, pos):
        card : Card = self.selected_card
        index : int = 0

        while(True):
            if(card == None):
                break
            card.rect.x = pos[0] + self.offset_x[index]
            card.rect.y = pos[1] + self.offset_y[index]
            index += 1
            card = card.children[0] if len(card.children) > 0 else None
        
    def get_possible_new_parent(self) -> Card:

        collided_cards = pygame.sprite.spritecollide(self.selected_card, layered_card_sprites, False)

        if(collided_cards == None or 
           (len(collided_cards) == 1 and collided_cards[0] == self.selected_card)):
            return None
        
        card: Card
        for card in collided_cards:
            if(card.children == None or len(card.children) == 0):
                return card

    def snap_selected_card_to_pos(self, rect: pygame.Rect):
        card : Card = self.selected_card
        card.update_position(rect.x, rect.y)

    def snap_pile_to_pos(self, rect: pygame.Rect):
        card : Card = self.selected_card

        while(True):
            if(card == None):
                break
            rect.y = rect.y + card_vertical_space
            card.update_position(rect.x, rect.y)
            card = card.children[0] if len(card.children) > 0 else None

    def snap_pile_to_original_position(self):
        card : Card = self.selected_card

        while(True):
            if(card == None):
                break
            card.rect = pygame.Rect(card.original_rect)
            card = card.children[0] if len(card.children) > 0 else None

    def get_picked_card(self, pos):
        vertical_pile_root = self.get_vertical_pile_root(pos[0])
        if(vertical_pile_root == None):
            return None
        
        # we got the vertical cascade pile now go deep using dps.
        stack : List[Card] = []
        current_card = vertical_pile_root

        while(True):
            if(current_card == None):
                break
            stack.append(current_card)
            current_card = current_card.children[0] if len(current_card.children) > 0 else None

        while(len(stack) > 0):
            current_card = stack.pop()

            if(current_card.rect.collidepoint(pos)):
                parent_card = stack.pop() if len(stack) > 0 else self.cascade_pile_root
                return current_card, parent_card
            
        return None

    # Get the root card of a cascade pile att the given x position.
    # returns a card if one is available else returns None in case the
    # cascade pile is empty or the x position does not fall within any cascade pile pos.
    def get_vertical_pile_root(self, pos_x) -> Card:
        for child in self.cascade_pile_root.children:
            if child.rect.left <= pos_x <= child.rect.right:
                return child            
        return None    
    
    def get_empty_free_cell_count(self) -> int:
        count : int = 0
        for i in range(len(self.free_cells)):
            if self.free_cells[i] == None:
                count += 1
        return count                
       
    def is_supermove_legit(self, destination_cascade_pile_index: int, moving_to_empty_cascade_pile=False) -> bool:
    # get total number of cards in the trail.
        card : Card = self.selected_card
        total_cards_in_trail: int = 0

        while True:
            if card == None:
                break
            total_cards_in_trail += 1
            card = card.children[0] if len(card.children) > 0 else None
        
    # get total empty cascade piles (excluding this one)
        total_empty_cascade_piles : int = 0
        for index in range (len(self.cascade_pile_root.children)):
            if self.cascade_pile_root.children[index] == None:
                if moving_to_empty_cascade_pile and destination_cascade_pile_index == index:
                    continue
                total_empty_cascade_piles += 1

    # get total empty free cells
        total_empty_free_cells : int = self.get_empty_free_cell_count()

    # cards in trail = 2^ecpX(efc+1)
        total_cards_allowed : int = (2**total_empty_cascade_piles) * (total_empty_free_cells+1)
        return total_cards_in_trail <= total_cards_allowed

    def add_to_previous_moves_list(self, move_data: MoveMetaData):
        if len(self.previous_moves_stack) >= total_previous_moves:
            self.previous_moves_stack.pop(0)
        self.previous_moves_stack.append(move_data)

    def pop_last_move(self): -> MoveMetaData:
        if len(self.previous_moves_stack) > 0:
            self.previous_moves_stack.pop()

    # Cards allowed to be moved at once = empty free cells + 1. So, if all 4 free cells are empty then trail of 5 cards can be moved
    # However, this number doubles for every empty cascade pile E.g.- 
    # 1. 4 free cells and 1 cascade pile then we can move 10 cards - 
    #       first 5 cards to the empty cascade pile using the 4 empty free cells
    #       next move remaining 5 to destination using the 4 empty free cells and 
    #       finally move the 5 cards that were moved to the empty cascade pile to the destination column using the 4 empty free cells
    # 2. If destination is the empty cascade pile itself and there are no other empty cascade piles then 
    #    only 5 cards can be moved for a total of 4 empty free cells    
    # 3. So we can say that cards allowed to be moved = 2^ECP X (EFC + 1), where
    #       ECP = number of empty cascade piles, EFC = number of empty free cells.
