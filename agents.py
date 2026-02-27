import pygame
import random
import math
from config import *

class Agent:    
    def __init__(self, x, y, speed, color):
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(
            random.uniform(-1, 1), 
            random.uniform(-1, 1)
        ).normalize()
        self.speed = speed
        self.color = color
        self.trail = []
        self.max_trail = 10
        
    def update_position(self, obstacles):
        avoidance = self.avoid_obstacles(obstacles)
        if avoidance.length() > 0:
            self.velocity = avoidance.normalize() #schimb directia agentului pt a evita obstacolul
        
        self.position += self.velocity * self.speed
        
        if self.position.x < 0 or self.position.x > WIDTH:
            self.velocity.x *= -1
        if self.position.y < 0 or self.position.y > HEIGHT:
            self.velocity.y *= -1
        #aici daca se loveste de margini, schimb directia
            
        self.position.x = max(0, min(self.position.x, WIDTH))
        self.position.y = max(0, min(self.position.y, HEIGHT))
        
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
    
    def avoid_obstacles(self, obstacles):
        avoidance = pygame.math.Vector2(0, 0)
        
        for obstacle in obstacles:
            distance = self.position.distance_to(obstacle.position)
            if distance < obstacle.radius + 30:  # 30 = distanta de evitare
                direction = (self.position - obstacle.position) # directia de la obstacol la agent
                if direction.length() > 0:
                    avoidance += direction.normalize() * (1 / max(distance, 1))
        
        return avoidance
    
    def draw_trail(self, screen):
        #Desenez urma agentului
        if len(self.trail) > 1:
            pygame.draw.lines(screen, self.color, False, 
                            [(int(p.x), int(p.y)) for p in self.trail], 1)


class Prey(Agent):    
    def __init__(self, x, y):
        super().__init__(x, y, BASE_PREY_SPEED, PREY_COLOR)
        self.energy = PREY_INITIAL_ENERGY
        self.reproduction_cooldown = 0
        self.vision = PREY_VISION
        self.food_vision = PREY_FOOD_VISION
        
    def update(self, predators, prey_list, food_list, obstacles):
        self.energy -= PREY_ENERGY_LOSS
        
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        
        nearest_predator = self.find_nearest(predators, self.vision)
        
        if nearest_predator:
            # PRIORITATE 1: Fugi de predator
            self.flee_from(nearest_predator)
        elif self.energy < 80:  
            # PRIORITATE 2: Cauta food
            nearest_food = self.find_nearest(food_list, self.food_vision)
            if nearest_food:
                self.move_towards(nearest_food)
        else:
            # PRIORITATE 3: Flocking 
            self.flock(prey_list)
        
        self.update_position(obstacles)
        
    def find_nearest(self, entities, vision_range):
        nearest = None
        min_dist = vision_range
        
        for entity in entities:
            if entity == self:
                continue
            dist = self.position.distance_to(entity.position)
            if dist < min_dist:
                min_dist = dist
                nearest = entity
        
        return nearest
    
    def flee_from(self, predator):
        flee_direction = (self.position - predator.position) #schimb directia pt a fugi
        if flee_direction.length() > 0:
            self.velocity = flee_direction.normalize()
    
    def move_towards(self, target): #opusul lui flee_from
        direction = (target.position - self.position)
        if direction.length() > 0:
            self.velocity = direction.normalize()
    
    def flock(self, prey_list):
        separation = pygame.math.Vector2(0, 0)
        alignment = pygame.math.Vector2(0, 0)
        cohesion = pygame.math.Vector2(0, 0)
        neighbors = 0
        
        for other in prey_list:
            if other == self:
                continue
                
            distance = self.position.distance_to(other.position)
            
            if distance < FLOCKING_RADIUS:
                neighbors += 1
                
                # Separation, evita aglomerarea, coliziunea
                if distance < 20:
                    separation += (self.position - other.position)
                
                # Alignment, da viteza 
                alignment += other.velocity
                
                # Cohesion, Mergi spre centrul grupului
                cohesion += other.position
        
        if neighbors > 0:
            alignment /= neighbors
            cohesion /= neighbors
            cohesion = (cohesion - self.position)
            
            # Aplic weight-uri
            separation *= SEPARATION_WEIGHT
            alignment *= ALIGNMENT_WEIGHT
            cohesion *= COHESION_WEIGHT
            
            steering = separation + alignment + cohesion
            if steering.length() > 0:
                self.velocity = steering.normalize()
            
            self.speed = BASE_PREY_SPEED + min(neighbors * FLOCK_SPEED_BONUS, 1.5)
        else:
            self.speed = BASE_PREY_SPEED
    
    def eat_food(self, food):
        self.energy = min(self.energy + PREY_ENERGY_GAIN_FOOD, PREY_MAX_ENERGY)
    
    def can_reproduce(self):
        return (self.energy >= PREY_REPRODUCTION_ENERGY and 
                self.reproduction_cooldown == 0)
    
    def reproduce(self):
        self.energy -= PREY_REPRODUCTION_COST
        self.reproduction_cooldown = PREY_REPRODUCTION_COOLDOWN
        
        # Offset mic pentru nou-nascut
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        
        return Prey(self.position.x + offset_x, self.position.y + offset_y)
    
    def is_alive(self):
        return self.energy > 0
    
    def draw(self, screen):
        if self.energy > 70:
            color = PREY_COLOR
        elif self.energy > 30:
            color = (200, 200, 50)  # Galben
        else:
            color = (255, 150, 50)  # Portocaliu
        
        pygame.draw.circle(screen, color, 
                         (int(self.position.x), int(self.position.y)), 5)
        self.draw_trail(screen)
        
        pygame.draw.rect(screen, (255, 0, 0), 
                        (int(self.position.x) - 10, int(self.position.y) - 15, 20, 3))
        pygame.draw.rect(screen, (0, 255, 0), 
                        (int(self.position.x) - 10, int(self.position.y) - 15, 
                         int(20 * (self.energy / PREY_MAX_ENERGY)), 3))


class Predator(Agent):    
    def __init__(self, x, y):
        super().__init__(x, y, BASE_PREDATOR_SPEED, PREDATOR_COLOR)
        self.energy = PREDATOR_INITIAL_ENERGY
        self.reproduction_cooldown = 0
        self.vision = PREDATOR_VISION
        
    def update(self, prey_list, predators, obstacles):
        self.energy -= PREDATOR_ENERGY_LOSS
        
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
        
        if prey_list:
            nearest_prey = self.find_nearest_prey(prey_list)
            if nearest_prey:
                self.hunt(nearest_prey)
        
        self.update_position(obstacles)
    
    def find_nearest_prey(self, prey_list):
        nearest = None
        min_dist = self.vision
        
        for prey in prey_list:
            dist = self.position.distance_to(prey.position)
            if dist < min_dist:
                min_dist = dist
                nearest = prey
        
        return nearest
    
    def hunt(self, prey):
        direction = (prey.position - self.position)
        if direction.length() > 0:
            self.velocity = direction.normalize()
    
    def eat_prey(self, prey):
        self.energy = min(self.energy + PREDATOR_ENERGY_GAIN_PREY, PREDATOR_MAX_ENERGY)
    
    def can_reproduce(self):
        return (self.energy >= PREDATOR_REPRODUCTION_ENERGY and 
                self.reproduction_cooldown == 0)
    
    def reproduce(self):
        self.energy -= PREDATOR_REPRODUCTION_COST
        self.reproduction_cooldown = PREDATOR_REPRODUCTION_COOLDOWN
        
        offset_x = random.randint(-20, 20)
        offset_y = random.randint(-20, 20)
        
        return Predator(self.position.x + offset_x, self.position.y + offset_y)
    
    def is_alive(self):
        return self.energy > 0
    
    def draw(self, screen):
        if self.energy > 100:
            color = PREDATOR_COLOR
        elif self.energy > 50:
            color = (200, 80, 80)
        else:
            color = (150, 50, 50)
        
        angle = self.velocity.angle_to(pygame.math.Vector2(1, 0))
        
        points = [
            pygame.math.Vector2(12, 0),
            pygame.math.Vector2(-6, -6),
            pygame.math.Vector2(-6, 6),
        ]
        
        rotated = [self.position + p.rotate(-angle) for p in points]
        pygame.draw.polygon(screen, color, rotated)
        self.draw_trail(screen)
        
        pygame.draw.rect(screen, (255, 0, 0), 
                        (int(self.position.x) - 12, int(self.position.y) - 18, 24, 3))
        pygame.draw.rect(screen, (0, 255, 0), 
                        (int(self.position.x) - 12, int(self.position.y) - 18, 
                         int(24 * (self.energy / PREDATOR_MAX_ENERGY)), 3))


class Food:    
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        self.radius = 4
        
    def draw(self, screen):
        pygame.draw.circle(screen, FOOD_COLOR, 
                         (int(self.position.x), int(self.position.y)), self.radius)


class Obstacle:    
    def __init__(self, x, y, radius):
        self.position = pygame.math.Vector2(x, y)
        self.radius = radius
        
    def draw(self, screen):
        pygame.draw.circle(screen, OBSTACLE_COLOR, 
                         (int(self.position.x), int(self.position.y)), 
                         self.radius, 2)  # 2 = grosime contur