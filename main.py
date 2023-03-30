import pygame
import sys
from time import perf_counter

pygame.init()

running = True


def quit():
    # closes pygame and quits the application
    pygame.quit()
    sys.exit(0)

delta_time = 1

# Main loop
while running:
    start_time = perf_counter()

    # Looping through events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()

        elif event.type == pygame.QUIT:
            quit()

    end_time = perf_counter()
    delta_time = end_time - start_time