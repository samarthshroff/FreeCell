# from tkinter import Tk
import pygame
from freecell import FreeCell
from freecell_canvas import FreeCellCanvas

if __name__ == "__main__":
   pygame.init()
   screen = pygame.display.set_mode((1450, 1000))
   clock = pygame.time.Clock()
   running = True
   dt = 0
   player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

   free_cell = FreeCell()
   free_cell.deal_new_game()
   free_cell_canvas = FreeCellCanvas(free_cell, screen)   
   # root = Tk()
   # root.title("FreeCell")


   while running:
      # poll for events
      # pygame.QUIT event means the user clicked X to close your window
      for event in pygame.event.get():
         free_cell.on_input(event)
         if event.type == pygame.QUIT:
               running = False

      screen.fill("white")
      free_cell_canvas.draw_ui()
      pygame.display.flip()
      dt = clock.tick(60)/100

   pygame.quit()
      
   # root.geometry("1500x1000")
   # root.mainloop()
