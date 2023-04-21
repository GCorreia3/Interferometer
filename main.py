import pygame
import sys
import math
from time import perf_counter

WIDTH = 800
HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.init()

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

def dist_to(pos1, pos2):
    return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)**0.5



def wavelength_to_colour(wavelength, amplitude):
    if wavelength >= 380 and wavelength <= 460:
        R = (460 - wavelength) / (460 - 350)
        G = 0
        B = 1
    elif wavelength >= 460 and wavelength <= 510:
        R = 0
        G = (wavelength - 460) / (510 - 460)
        B = 1
    elif wavelength >= 510 and wavelength <= 550:
        R = 0
        G = 1
        B = (550 - wavelength) / (550 - 510)
    elif wavelength >= 550 and wavelength <= 600:
        R = (wavelength - 550) / (600 - 550)
        G = 1
        B = 0
    elif wavelength >= 600 and wavelength <= 700:
        R = 1
        G = (700 - wavelength) / (700 - 600)
        B = 0
    else:
        R = 1
        G = 1
        B = 1

    return (int(R * 255 * amplitude), int(G * 255 * amplitude), int(B * 255 * amplitude))



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

        self.time_distorting = 0

        if self.drag_axis == 0:
            self.path_distance = self.pos[0] - WIDTH/2
        else:
            self.path_distance = HEIGHT/2 - self.pos[1]

    def update(self, delta_time, mouse, distorting):
        if distorting:
            if self.drag_axis == 0:
                self.pos = (self.pos[0] + math.cos(self.time_distorting) * delta_time * 50, self.pos[1])
                self.path_distance = self.pos[0] - WIDTH/2

            else:
                self.pos = (self.pos[0], self.pos[1] + math.cos(self.time_distorting) * delta_time * 50)
                self.path_distance = HEIGHT/2 - self.pos[1]

            self.rect.center = self.pos
            self.time_distorting += delta_time
        else:
            self.time_distorting = 0
            if mouse:
                if self.drag:
                    if self.drag_axis == 0:
                        self.pos = (min(self.max_pos, max(self.min_pos, mouse[0] + self.drag_offset[0])), self.pos[1])
                        self.path_distance = self.pos[0] - WIDTH/2
                    else:
                        self.pos = (self.pos[0], min(self.max_pos, max(self.min_pos, mouse[1] + self.drag_offset[1])))
                        self.path_distance = HEIGHT/2 - self.pos[1]

                    self.rect.center = self.pos



class Laser():
    def __init__(self, pos, width, length, amplitude, wavelength, direction) -> None:

        self.x, self.y = pos
        self.width = width
        self.length = length

        self.amplitude = amplitude

        self.wavelength = wavelength
        self.speed = 3_000_000_000
        self.frequency = self.speed / (wavelength / 1_000_000_000)

        self.colour = wavelength_to_colour(self.wavelength, self.amplitude)

        self.direction = direction

    def update_length(self, mirror_position):
        self.length = dist_to((self.x, self.y), mirror_position)

    def update_amplitude(self, phase_difference):
        self.amplitude = phase_difference
        self.colour = wavelength_to_colour(self.wavelength, self.amplitude)

    def draw(self):
        if self.direction == UP:
            pygame.draw.rect(WIN, self.colour, (self.x - self.width/2, self.y - self.length, self.width, self.length))
        elif self.direction == RIGHT:
            pygame.draw.rect(WIN, self.colour, (self.x, self.y - self.width/2, self.length, self.width))
        elif self.direction == DOWN:
            pygame.draw.rect(WIN, self.colour, (self.x - self.width/2, self.y, self.width, self.length))
        elif self.direction == LEFT:
            pygame.draw.rect(WIN, self.colour, (self.x - self.length, self.y - self.width/2, self.length, self.width))



class Interferometer():
    def __init__(self, wavelength) -> None:

        self.split_mirror = RotatedRectangle((WIDTH/2, HEIGHT/2), 50, 10, 45, (100, 200, 255))

        self.top_mirror = Mirror((WIDTH/2, HEIGHT/8), 50, 10, 0, (100, 200, 255), 1, 5, HEIGHT/2-25)
        self.right_mirror = Mirror((7*WIDTH/8, HEIGHT/2), 50, 10, 90, (100, 200, 255), 0, WIDTH/2+25, WIDTH-5)

        self.wavelength = wavelength

        self.laser_emitted = Laser((WIDTH/4-25 + 50, HEIGHT/2-25/2 + 12.5), 10, dist_to((WIDTH/4-25 + 50, HEIGHT/2-25/2 + 12.5), self.right_mirror.pos), 0.5, self.wavelength, RIGHT)
        self.split_laser = Laser((WIDTH/2, HEIGHT/2), 10, dist_to((WIDTH/2, HEIGHT/2), self.top_mirror.pos), 0.5, self.wavelength, UP)
        self.resultant_laser = Laser((WIDTH/2, HEIGHT/2), 10, dist_to((WIDTH/2, HEIGHT/2), (WIDTH/2-25/2, 3*HEIGHT/4-25/2)), 0.5, self.wavelength, DOWN)

        self.path_difference = abs(self.top_mirror.path_distance - self.right_mirror.path_distance)

        self.phase_difference = abs(abs(((self.path_difference % self.wavelength) / self.wavelength) - 0.5) - 0.5) * 2 # 1 if in phase, 0 if not

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

    def update(self, delta_time, mouse, distorting):
        self.top_mirror.update(delta_time, mouse, distorting)
        self.right_mirror.update(delta_time, mouse, distorting)

        self.path_difference = abs(self.top_mirror.path_distance - self.right_mirror.path_distance)

        self.phase_difference = abs(abs(((self.path_difference % self.wavelength) / self.wavelength) - 0.5) - 0.5) * 2

        self.laser_emitted.update_length(self.right_mirror.pos)
        self.split_laser.update_length(self.top_mirror.pos)
        self.resultant_laser.update_amplitude(self.phase_difference)
    
    def draw(self):
        # Draw Laser Emitter
        pygame.draw.rect(WIN, (255, 255, 255), (WIDTH/4-25, HEIGHT/2-25/2, 50, 25))

        # Draw Detector
        pygame.draw.rect(WIN, (255, 255, 255), (WIDTH/2-25/2, 3*HEIGHT/4-25/2, 25, 25))

        # Draw lasers
        self.laser_emitted.draw()
        self.split_laser.draw()
        self.resultant_laser.draw()

        # Draw Two Mirrors
        self.top_mirror.draw()
        self.right_mirror.draw()

        # Draw Splitter Mirror
        self.split_mirror.draw()



running = True
distorting = False

interferometer = Interferometer(wavelength=700)

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

    mouse = None

    # Looping through events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()
            if event.key == pygame.K_SPACE:
                distorting = not distorting

        elif event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.mouse.get_pos()
            interferometer.check_drag(mouse)

        elif event.type == pygame.MOUSEMOTION:
            mouse = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            interferometer.stop_drag()

    interferometer.update(delta_time, mouse, distorting)

    pygame.display.update()

    end_time = perf_counter()
    delta_time = end_time - start_time