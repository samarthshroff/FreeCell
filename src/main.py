# from tkinter import Tk
from tkinter import PhotoImage

import pygame
from freecell import FreeCell
from freecell_canvas import FreeCellCanvas
from threading import Timer



if __name__ == "__main__":
   show_game: bool = False
   pygame.init()
   screen = pygame.display.set_mode((1500, 1100))
   logo = pygame.image.load("images/splash.png")
   logo = pygame.transform.scale(logo, (1500,1100))  # Resize to fit screen

   clock = pygame.time.Clock()
   running = True
   dt = 0
   player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

   free_cell = FreeCell()
   free_cell.deal_new_game()
   free_cell_canvas = FreeCellCanvas(free_cell, screen)   

   start_time = pygame.time.get_ticks()
   while running:
      # poll for events
      # pygame.QUIT event means the user clicked X to close your window
      for event in pygame.event.get():
         free_cell.on_input(event)
         if event.type == pygame.QUIT:
               running = False
      if show_game is False:
         screen.blit(logo, (0,0))
      else:
         screen.fill("white")
         free_cell_canvas.draw_ui()

      pygame.display.flip()
      # Check elapsed time
      if pygame.time.get_ticks() - start_time >= 5 * 1000:
         show_game = True
      dt = clock.tick(60) / 100


   pygame.quit()
