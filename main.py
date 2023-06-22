import pygame
import sys
import math
from time import perf_counter

WIDTH = 800
HEIGHT = 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.init()

font = pygame.font.SysFont("calibri", 20)

def dist_to(pos1, pos2):
    return ((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)**0.5



def wavelength_to_colour(wavelength, amplitude):
    if realistic:
        amplitude = 1
    if wavelength >= 380 and wavelength <= 460:
        R = (460 - wavelength) / (460 - 380)
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
    
    return (int(R * 255 * min(1, amplitude)), int(G * 255 * min(1, amplitude)), int(B * 255 * min(1, amplitude)))



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



class Toggle():
    def __init__(self, pos, width, height, text, box_colour, condition: bool) -> None:
        self.pos = pos
        self.width = width
        self.height = height

        self.text = text

        self.box_colour = box_colour

        self.condition = condition

        self.toggle_offset = 5

    def check_click(self, mouse):
        if abs(mouse[0] - self.pos[0]) <= self.width/2 and abs(mouse[1] - self.pos[1]) <= self.height/2:
            self.condition = not self.condition
        
        return self.condition

    def draw(self):
        # Draw background rectangle
        pygame.draw.rect(WIN, self.box_colour, (self.pos[0] - self.width/2, self.pos[1] - self.height/2, self.width, self.height), 2)

        # Draw toggle
        if self.condition:
            pygame.draw.rect(WIN, (0, 255, 0), (self.pos[0] - self.width/2 + self.toggle_offset, self.pos[1] - self.height/2 + self.toggle_offset, self.width - 2*self.toggle_offset, self.height - 2*self.toggle_offset))

        # Draw toggle text
        text_surface = font.render(self.text, True, (255, 255, 255))
        WIN.blit(text_surface, (self.pos[0] + self.width, self.pos[1] - text_surface.get_height()/2))



class Graph():
    def __init__(self, pos, width, height, colour, x_start, x_end, y_start, y_end) -> None:
        self.pos = pos
        self.width = width
        self.height = height
        self.colour = colour

        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end

        self.x_range = x_end - x_start
        self.y_range = y_end - y_start

        self.axis_offset = 25

        self.start_y_coords = (self.pos[0] - self.width/2 + self.axis_offset, self.pos[1] + self.height/2 - self.axis_offset)
        self.end_y_coords = (self.pos[0] - self.width/2 + self.axis_offset, self.pos[1] - self.height/2 + self.axis_offset)

        self.start_x_coords = (self.pos[0] - self.width/2 + self.axis_offset, self.pos[1] + self.height/2 - self.axis_offset)
        self.end_x_coords = (self.pos[0] + self.width/2 - self.axis_offset, self.pos[1] + self.height/2 - self.axis_offset)

        self.x_coord_range = self.end_x_coords[0] - self.start_x_coords[0]
        self.y_coord_range = self.end_y_coords[1] - self.start_y_coords[1]

        self.points = []

        self.text_offset = 5

        self.x_axis_title = "Time/s"
        self.y_axis_title = "Intensity"

        self.x_axis_grid_separation = 1
        self.y_axis_grid_separation = 0.25

        self.is_graphing_colour = (255, 0, 0)

        self.graph_timer = 0
        self.graph_time = 0.1
        self.graph_total_time = 0

    def point_to_position(self, point):

        x_proportion = point[0] / self.x_range
        new_x = x_proportion * self.x_coord_range

        y_proportion = point[1] / self.y_range
        new_y = y_proportion * self.y_coord_range

        return (self.start_x_coords[0] + new_x, self.start_y_coords[1] + new_y)
    
    def add_point(self, point):
        self.points.append(point)

    def draw_axis_info(self):
        # Draw x-axis labels
        axis_x_start = font.render(f"{self.x_start}", True, (255, 255, 255))
        WIN.blit(axis_x_start, (self.start_x_coords[0] - axis_x_start.get_width()/2, self.start_x_coords[1] + self.text_offset))

        axis_x_end = font.render(f"{round(self.x_end, 2)}", True, (255, 255, 255))
        WIN.blit(axis_x_end, (self.end_x_coords[0] - axis_x_end.get_width()/2, self.end_x_coords[1] + self.text_offset))

        # Draw y-axis labels
        axis_y_start = font.render(f"{self.y_start}", True, (255, 255, 255))
        WIN.blit(axis_y_start, (self.start_y_coords[0] - axis_y_start.get_width() - self.text_offset, self.start_y_coords[1] - axis_y_start.get_height()/2))

        axis_y_end = font.render(f"{self.y_end}", True, (255, 255, 255))
        WIN.blit(axis_y_end, (self.end_y_coords[0] - axis_y_end.get_width() - self.text_offset, self.end_y_coords[1]))

        # Draw x-axis Title
        axis_x_title = font.render(self.x_axis_title, True, (255, 255, 255))
        WIN.blit(axis_x_title, (self.pos[0] - axis_x_title.get_width()/2, self.start_x_coords[1] + self.text_offset))

        # Draw y-axis Title
        axis_y_title = font.render(self.y_axis_title, True, (255, 255, 255))
        axis_y_title = pygame.transform.rotate(axis_y_title, 90)
        WIN.blit(axis_y_title, (self.start_y_coords[0] - axis_y_title.get_width()/2 - self.text_offset - 5, self.pos[1] - axis_y_title.get_height()/2))

    def update(self, delta_time, graphing, phase_difference, amplitude):
        if graphing:
            self.is_graphing_colour = (0, 255, 0)
            if self.graph_timer < self.graph_time:
                self.graph_timer += delta_time
                self.graph_total_time += delta_time
            else:
                self.add_point((self.graph_total_time, phase_difference * amplitude * 2))
                self.graph_timer = 0

            self.x_end = max(30, self.graph_total_time)
            self.x_range = self.x_end - self.x_start
        else:
            self.is_graphing_colour = (255, 0, 0)

    def draw(self):
        # Draws background
        pygame.draw.rect(WIN, self.colour, (self.pos[0] - self.width/2, self.pos[1] - self.height/2, self.width, self.height))

        # X-axis
        pygame.draw.line(WIN, (255, 255, 255), self.start_x_coords, self.end_x_coords)

        # Y-axis
        pygame.draw.line(WIN, (255, 255, 255), self.start_y_coords, self.end_y_coords)


        # Draw grid
        num_x_lines = self.x_range / self.x_axis_grid_separation
        if num_x_lines > 20:
            self.x_axis_grid_separation *= 2
            num_x_lines = self.x_range / self.x_axis_grid_separation
        
        for x in range(int(num_x_lines)):
            pygame.draw.line(WIN, (100, 100, 100), (self.start_y_coords[0] + (x+1)/(self.x_range / self.x_axis_grid_separation) * self.x_coord_range, self.start_y_coords[1]), (self.end_y_coords[0] + (x+1)/(self.x_range / self.x_axis_grid_separation) * self.x_coord_range, self.end_y_coords[1]))
        
        for y in range(int(self.y_range / self.y_axis_grid_separation)):
            pygame.draw.line(WIN, (100, 100, 100), (self.start_x_coords[0], self.start_x_coords[1] + (y+1)/(self.y_range / self.y_axis_grid_separation) * self.y_coord_range), (self.end_x_coords[0], self.end_x_coords[1] + (y+1)/(self.y_range / self.y_axis_grid_separation) * self.y_coord_range))

        
        # Draw is graphing circle
        pygame.draw.circle(WIN, self.is_graphing_colour, (self.pos[0] + self.width/2 - 7, self.pos[1] - self.height/2 + 7), 7)
        

        # Draws points
        if len(self.points) > 1:

            # Remove close points to improve performance
            if dist_to(self.point_to_position(self.points[len(self.points)-1]), self.point_to_position(self.points[len(self.points)-2])) < 1:
                self.points.remove(self.points[len(self.points)-1])

            for i in range(len(self.points) - 1):
                pygame.draw.line(WIN, (100, 100, 255), self.point_to_position(self.points[i]), self.point_to_position(self.points[i+1]), 2)

            # Draws info on last point
            info_text = font.render(f"{round(self.points[len(self.points)-1][1], 2)}", True, (255, 255, 255))
            WIN.blit(info_text, (self.point_to_position(self.points[len(self.points)-1])[0] + info_text.get_width()/2, self.point_to_position(self.points[len(self.points)-1])[1] - info_text.get_height()/2))
        
        #for point in self.points:
            #pygame.draw.circle(WIN, (255, 255, 255), self.point_to_position(point), 5)

        # Draws axis
        self.draw_axis_info()



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

    def update_pos(self, pos):
        self.pos = pos
        self.rect.center = pos

    def update(self, delta_time, mouse, distorting):
        if distorting:
            if self.drag_axis == 0:
                self.update_pos((self.pos[0] + math.cos(self.time_distorting) * delta_time * 50, self.pos[1]))

            else:
                self.update_pos((self.pos[0], self.pos[1] + math.cos(self.time_distorting) * delta_time * 50))

            self.time_distorting += delta_time
        else:
            self.time_distorting = 0
            if mouse and self.drag:
                if self.drag_axis == 0:
                    self.update_pos((min(self.max_pos, max(self.min_pos, mouse[0] + self.drag_offset[0])), self.pos[1]))
                else:
                    self.update_pos((self.pos[0], min(self.max_pos, max(self.min_pos, mouse[1] + self.drag_offset[1]))))
            
        if self.drag_axis == 0:
            self.path_distance = self.pos[0] - WIDTH/2
        else:
            self.path_distance = HEIGHT/2 - self.pos[1]



class Laser():
    def __init__(self, start_pos, end_pos, width, amplitude, wavelength, phase=0) -> None:

        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.width = width

        self.amplitude = amplitude

        self.wavelength = wavelength
        self.speed = 3_000_000_000
        self.frequency = self.speed / (wavelength / 1_000_000_000)

        self.colour = wavelength_to_colour(self.wavelength, self.amplitude)

        self.path_distance = 0
        self.phase = phase

        self.laser_points = []

    def update_amplitude(self, phase_difference):
        self.amplitude = phase_difference
        self.colour = wavelength_to_colour(self.wavelength, self.amplitude)

    def draw(self):
        if not realistic:
            pygame.draw.line(WIN, self.colour, (self.start_x, self.start_y), (self.end_x, self.end_y), self.width)
        else:
            length = dist_to((self.start_x, self.start_y), (self.end_x, self.end_y))
            x_difference = self.end_x - self.start_x
            y_difference = self.end_y - self.start_y
            angle = math.atan2(y_difference, x_difference)
            self.laser_points.clear()
            for i in range(int(length / 5) + 1):
                self.laser_points.append((self.start_x + (i * 5) * math.cos(angle) + (self.amplitude * 10 * math.sin((i*5 / self.wavelength) * 2*math.pi + self.phase)) * math.sin(angle)
                                        , self.start_y + (i * 5) * math.sin(angle) + (self.amplitude * 10 * math.sin((i*5 / self.wavelength) * 2*math.pi + self.phase)) * math.cos(angle)))

            if len(self.laser_points) > 1:
                pygame.draw.lines(WIN, self.colour, False, self.laser_points, self.width)



class Interferometer():
    def __init__(self, wavelength, amplitude) -> None:

        self.split_mirror = RotatedRectangle((WIDTH/2, HEIGHT/2), 50, 10, 45, (100, 200, 255))

        self.top_mirror = Mirror((WIDTH/2, HEIGHT/8), 50, 10, 0, (100, 200, 255), 1, 5, HEIGHT/2-25)
        self.right_mirror = Mirror((7*WIDTH/8, HEIGHT/2), 50, 10, 90, (100, 200, 255), 0, WIDTH/2+25, WIDTH-5)

        self.wavelength = wavelength
        self.amplitude = amplitude

        self.laser_emitted = Laser((WIDTH/4+25, HEIGHT/2), self.right_mirror.pos, 4, self.amplitude, self.wavelength)
        self.split_laser = Laser((WIDTH/2, HEIGHT/2), self.top_mirror.pos, 4, self.amplitude, self.wavelength)
        self.resultant_laser = Laser((WIDTH/2, HEIGHT/2), (WIDTH/2, 2.5*HEIGHT/4-25/2), 4, self.amplitude, self.wavelength)

        self.reflected_right_laser = Laser(self.right_mirror.pos, (WIDTH/2, HEIGHT/2), 2, self.amplitude, self.wavelength, phase=math.pi)
        self.reflected_top_laser = Laser(self.top_mirror.pos, (WIDTH/2, HEIGHT/2), 2, self.amplitude, self.wavelength, phase=math.pi)

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

    def reset_mirrors(self):
        self.top_mirror.update_pos((WIDTH/2, HEIGHT/8))
        self.right_mirror.update_pos((7*WIDTH/8, HEIGHT/2))

    def update(self, delta_time, mouse, distorting):
        self.top_mirror.update(delta_time, mouse, distorting)
        self.right_mirror.update(delta_time, mouse, distorting)

        self.path_difference = abs(self.top_mirror.path_distance - self.right_mirror.path_distance)

        self.phase_difference = abs(abs(((self.path_difference % self.wavelength) / self.wavelength) - 0.5) - 0.5) * 2

        self.laser_emitted.path_distance = self.right_mirror.path_distance
        self.split_laser.path_distance = self.top_mirror.path_distance

        self.laser_emitted.end_x, self.laser_emitted.end_y = self.right_mirror.pos
        self.split_laser.end_x, self.split_laser.end_y = self.top_mirror.pos
        self.resultant_laser.update_amplitude(self.phase_difference * self.amplitude * 2)

        right_end_phase = (self.right_mirror.path_distance % self.wavelength) / self.wavelength * 2*math.pi

        self.reflected_right_laser.start_x, self.reflected_right_laser.start_y = self.right_mirror.pos
        self.reflected_right_laser.phase = (right_end_phase + math.pi) % 2*math.pi

        top_end_phase = (self.top_mirror.path_distance % self.wavelength) / self.wavelength * 2*math.pi

        self.reflected_top_laser.start_x, self.reflected_top_laser.start_y = self.top_mirror.pos
        self.reflected_top_laser.phase = (top_end_phase + math.pi) % 2*math.pi

        self.resultant_laser.phase = (self.path_difference % self.wavelength) / self.wavelength * 2*math.pi
    
    def draw(self):
        # Draw lasers
        self.resultant_laser.draw()
        self.laser_emitted.draw()
        self.split_laser.draw()

        self.reflected_right_laser.draw()
        self.reflected_top_laser.draw()

        # Draw Two Mirrors
        self.top_mirror.draw()
        self.right_mirror.draw()

        # Draw Splitter Mirror
        self.split_mirror.draw()

        # Draw Laser Emitter
        pygame.draw.rect(WIN, (255, 255, 255), (WIDTH/4-25, HEIGHT/2-25/2, 50, 25))

        # Draw Detector
        pygame.draw.rect(WIN, (255, 255, 255), (WIDTH/2-25/2, 2.5*HEIGHT/4-25/2, 25, 25))



running = True
distorting = False
realistic = False

interferometer = Interferometer(wavelength=400, amplitude=0.5)
graph = Graph((WIDTH/2, HEIGHT-125), WIDTH*3.5/4, 250, (10, 10, 15), x_start=0, x_end=30, y_start=0, y_end=1)
realistic_toggle = Toggle((WIDTH - 100, 25), 25, 25, "Realistic", (255, 255, 255), realistic)

def quit():
    # closes pygame and quits the application
    pygame.quit()
    sys.exit(0)



average_fps_elapsed_time = 0
average_fps = 0
n_fps = 1
showing_average_fps = 0
def get_average_fps(delta_time):

    global average_fps_elapsed_time, average_fps, n_fps, showing_average_fps
    average_fps_elapsed_time += delta_time
    if average_fps_elapsed_time > 0.2:

        average_fps_elapsed_time = 0
        showing_average_fps = average_fps
        average_fps = 1 / delta_time
        n_fps = 1

    else:
        average_fps = (1 / delta_time + n_fps * average_fps) / (n_fps + 1)
        n_fps += 1

    return showing_average_fps



delta_time = 1

graphing = False

# Main loop
while running:
    start_time = perf_counter()

    WIN.fill((0, 0, 0))

    interferometer.draw()
    graph.draw()
    realistic_toggle.draw()
    
    # Fps text
    fps_text = font.render(f"FPS: {round(get_average_fps(delta_time))}", True, (255, 255, 255))
    WIN.blit(fps_text, (0, 0))

    mouse = None

    # Looping through events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()

            if event.key == pygame.K_SPACE:
                distorting = not distorting

            if event.key == pygame.K_g:
                graphing = not graphing

            if event.key == pygame.K_r:
                # Resets everything
                graph.points.clear()

                if graphing:
                    graphing = False
                
                if distorting:
                    distorting = False

                interferometer.reset_mirrors()

                graph.graph_total_time = 0

            if event.key == pygame.K_s:
                # Save data to file
                data = open("data.txt", "w")
                for point in graph.points:
                    data.write(f"Time: {round(point[0], 6)}         Intensity: {round(point[1], 6)}\n")
                data.close()


        elif event.type == pygame.QUIT:
            quit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse = pygame.mouse.get_pos()
            interferometer.check_drag(mouse)

            realistic = realistic_toggle.check_click(mouse)

        elif event.type == pygame.MOUSEMOTION:
            mouse = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            interferometer.stop_drag()

    interferometer.update(delta_time, mouse, distorting)

    graph.update(delta_time, graphing, interferometer.phase_difference, interferometer.amplitude)

    pygame.display.update()

    end_time = perf_counter()
    delta_time = end_time - start_time