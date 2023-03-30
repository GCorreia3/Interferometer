import pygame
import sys
from time import perf_counter

WIDTH = 800
HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.init()

running = True



def dist_to(pos1, pos2):
    return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)**0.5



class RotatedRectangle():
    def __init__(self, pos, width, height, rotation, colour) -> None:
        
        self.pos = pos # tuple of x and y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.colour = colour
        
        self.original_image = pygame.Surface((self.width, self.height))
        self.original_image.set_colorkey((0, 0, 0)) # for making transparent background while rotating an image
        self.original_image.fill(self.colour)

        self.rect = self.original_image.get_rect()
        self.rect.center = self.pos

    def draw(self):
        if self.rotation != 0:
            old_center = self.rect.center

            new_image = pygame.transform.rotate(self.original_image, self.rotation)

            rect = new_image.get_rect()
            rect.center = old_center

            WIN.blit(new_image, rect)
        else:
            WIN.blit(self.original_image, self.rect)



class Mirror(RotatedRectangle):
    def __init__(self, pos, width, height, rotation, colour, drag_axis, min_pos, max_pos) -> None:
        super().__init__(pos, width, height, rotation, colour)

        self.drag = False
        self.drag_axis = drag_axis # 0 for x-axis, 1 for y-axis
        self.drag_offset = (0, 0)

        self.min_pos = min_pos
        self.max_pos = max_pos

        if self.drag_axis == 0:
            self.path_distance = self.pos[0] - WIDTH/2
        else:
            self.path_distance = HEIGHT/2 - self.pos[1]

    def update(self, mouse):
        if self.drag:
            if self.drag_axis == 0:
                self.pos = (min(self.max_pos, max(self.min_pos, mouse[0] + self.drag_offset[0])), self.pos[1])
                self.path_distance = self.pos[0] - WIDTH/2
            else:
                self.pos = (self.pos[0], min(self.max_pos, max(self.min_pos, mouse[1] + self.drag_offset[1])))
                self.path_distance = HEIGHT/2 - self.pos[1]

            self.rect.center = self.pos



class Interferometer():
    def __init__(self) -> None:

        self.split_mirror = RotatedRectangle((WIDTH/2, HEIGHT/2), 50, 10, 45, (100, 200, 255))

        self.top_mirror = Mirror((WIDTH/2, HEIGHT/8), 50, 10, 0, (100, 200, 255), 1, 5, HEIGHT/2-25)
        self.right_mirror = Mirror((7*WIDTH/8, HEIGHT/2), 50, 10, 90, (100, 200, 255), 0, WIDTH/2+25, WIDTH-5)

        self.path_difference = abs(self.top_mirror.path_distance - self.right_mirror.path_distance)

        self.wavelength = 100

        self.phase_difference = abs(abs(((self.path_difference % self.wavelength) / self.wavelength) - 0.5) - 0.5) * 2

    def check_drag(self, mouse):
        if dist_to(self.top_mirror.pos, mouse) < self.top_mirror.width:
            self.top_mirror.drag = True
            self.top_mirror.drag_offset = (self.top_mirror.pos[0] - mouse[0], self.top_mirror.pos[1] - mouse[1])
        elif dist_to(self.right_mirror.pos, mouse) < self.right_mirror.width:
            self.right_mirror.drag = True
            self.right_mirror.drag_offset = (self.right_mirror.pos[0] - mouse[0], self.right_mirror.pos[1] - mouse[1])

    def stop_drag(self):
        self.top_mirror.drag = False
        self.right_mirror.drag = False

    def update(self, mouse):
        self.top_mirror.update(mouse)
        self.right_mirror.update(mouse)

        self.path_difference = abs(self.top_mirror.path_distance - self.right_mirror.path_distance)

        self.phase_difference = abs(abs(((self.path_difference % self.wavelength) / self.wavelength) - 0.5) - 0.5) * 2
    
    def draw(self):
        # Draw Laser Emitter
        pygame.draw.rect(WIN, (255, 255, 255), (WIDTH/4-25, HEIGHT/2-25/2, 50, 25))

        # Draw Detector
        pygame.draw.rect(WIN, (255, 255, 255), (WIDTH/2-25/2, 3*HEIGHT/4-25/2, 25, 25))

        # Draw First Laser
        pygame.draw.rect(WIN, (255, 0, 0), (WIDTH/4+25, HEIGHT/2-5, WIDTH/4-25, 10))

        # Draw Both Split Lasers
        pygame.draw.rect(WIN, (255/2, 0, 0), (WIDTH/2, HEIGHT/2-5, self.right_mirror.pos[0]-WIDTH/2, 10))
        pygame.draw.rect(WIN, (255/2, 0, 0), (WIDTH/2-5, self.top_mirror.pos[1], 10, HEIGHT/2-self.top_mirror.pos[1]))

        # Draw Resultant Laser
        pygame.draw.rect(WIN, (255 * self.phase_difference, 0, 0), (WIDTH/2-5, HEIGHT/2, 10, HEIGHT/4-25/2))

        # Draw Two Mirrors
        self.top_mirror.draw()
        self.right_mirror.draw()

        # Draw Splitter Mirror
        self.split_mirror.draw()



interferometer = Interferometer()

def quit():
    # closes pygame and quits the application
    pygame.quit()
    sys.exit(0)

delta_time = 1

# Main loop
while running:
    start_time = perf_counter()

    WIN.fill((0, 0, 0))

    interferometer.draw()

    # Looping through events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()

        elif event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.mouse.get_pos()
            interferometer.check_drag(mouse)

        elif event.type == pygame.MOUSEMOTION:
            mouse = pygame.mouse.get_pos()
            interferometer.update(mouse)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            interferometer.stop_drag()

    pygame.display.update()

    end_time = perf_counter()
    delta_time = end_time - start_time