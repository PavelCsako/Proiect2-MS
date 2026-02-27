import pygame
import random
from config import *
from agents import Prey, Predator, Food, Obstacle
from visualizer import SimulationVisualizer

class Simulation:
    
    def __init__(self):
        pygame.init() #porniea motorului :))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Predator-Prey Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 32)
        
        #liste pt agenti
        self.prey_list = []
        self.predator_list = []
        self.food_list = []
        self.obstacles = []
        
        #contoare pt statisitici
        self.prey_births_this_frame = 0
        self.predator_births_this_frame = 0
        self.total_prey_births = 0
        self.total_predator_births = 0
        self.total_prey_deaths = 0
        self.total_predator_deaths = 0
        
        #counter pentru spawn food
        self.food_spawn_timer = 0
        
        # creez vizualizatorul pentru grafice
        self.visualizer = SimulationVisualizer()
        
        self.running = True
        self.paused = False
        
        self.reset_simulation()
    
    def reset_simulation(self): #ca un fel de nou joc
        self.prey_list = [
            Prey(random.randint(50, WIDTH-50), 
                 random.randint(50, HEIGHT-50))
            for _ in range(INITIAL_PREY)
        ]
        
        self.predator_list = [
            Predator(random.randint(50, WIDTH-50), 
                     random.randint(50, HEIGHT-50))
            for _ in range(INITIAL_PREDATORS)
        ]
        
        self.food_list = [
            Food(random.randint(20, WIDTH-20), 
                 random.randint(20, HEIGHT-20))
            for _ in range(INITIAL_FOOD)
        ]
        
        self.obstacles = [
            Obstacle(random.randint(100, WIDTH-100), 
                    random.randint(100, HEIGHT-100),
                    random.randint(30, 60))
            for _ in range(INITIAL_OBSTACLES)
        ]
        
        self.total_prey_births = 0
        self.total_predator_births = 0
        self.total_prey_deaths = 0
        self.total_predator_deaths = 0
        
        self.visualizer = SimulationVisualizer()
        #Creez un visualizer nou (sterg istoricul vechi).

        print("Simulation reset!")
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            
            self.handle_events() #verific input-ul
            
            if not self.paused:
                self.update()
            
            self.render() #desenez totul pe ecran
        
        # La final, arată graficele
        print("\nGenerare grafice...")
        self.visualizer.plot_graphs()
        self.visualizer.save_data()
        
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print(f"{'PAUSED' if self.paused else 'RESUMED'}")
                
                # R = Reset
                elif event.key == pygame.K_r:
                    self.reset_simulation()
                
                # G = Show graphs 
                elif event.key == pygame.K_g:
                    print("Afișare grafice...")
                    self.visualizer.plot_graphs()
                
                # P = Add Prey
                elif event.key == pygame.K_p:
                    self.prey_list.append(
                        Prey(random.randint(50, WIDTH-50), 
                             random.randint(50, HEIGHT-50))
                    )
                
                # O = Add Predator
                elif event.key == pygame.K_o:
                    self.predator_list.append(
                        Predator(random.randint(50, WIDTH-50), 
                                random.randint(50, HEIGHT-50))
                    )
                
                # F = Add Food
                elif event.key == pygame.K_f:
                    for _ in range(5):  # Adaug 5 bucati
                        self.food_list.append(
                            Food(random.randint(20, WIDTH-20), 
                                random.randint(20, HEIGHT-20))
                        )
                
                # B = Add Obstacle
                elif event.key == pygame.K_b:
                    mx, my = pygame.mouse.get_pos()
                    self.obstacles.append(Obstacle(mx, my, random.randint(30, 60)))
                
                # C = Clear Obstacles
                elif event.key == pygame.K_c:
                    self.obstacles.clear()
    
    def update(self):
        self.prey_births_this_frame = 0
        self.predator_births_this_frame = 0
        
        self.update_prey()
        
        self.update_predators()
        
        self.spawn_food()
        
        #salvez datele pentru grafice, in visualizator
        #trimit listele curente si nasterile din frame-ul asta
        self.visualizer.update_history(
            self.prey_list,
            self.predator_list,
            self.food_list,
            self.prey_births_this_frame,
            self.predator_births_this_frame
        )
    
    def update_prey(self):
        for prey in self.prey_list[:]: #parcurg o copie a listei
            prey.update(self.predator_list, self.prey_list, 
                       self.food_list, self.obstacles)
            
            if not prey.is_alive():
                self.prey_list.remove(prey)
                self.total_prey_deaths += 1
                continue
            
            for food in self.food_list[:]:
                if prey.position.distance_to(food.position) < 10:
                    prey.eat_food(food)
                    self.food_list.remove(food)
                    break
            
            if prey.can_reproduce():
                for other in self.prey_list:
                    if other == prey:
                        continue
                    if (other.can_reproduce() and 
                        prey.position.distance_to(other.position) < 30):
                        baby = prey.reproduce()
                        other.reproduction_cooldown = PREY_REPRODUCTION_COOLDOWN
                        self.prey_list.append(baby)
                        self.prey_births_this_frame += 1
                        self.total_prey_births += 1
                        break
    
    def update_predators(self):
        for predator in self.predator_list[:]:
            predator.update(self.prey_list, self.predator_list, self.obstacles)
            
            if not predator.is_alive():
                self.predator_list.remove(predator)
                self.total_predator_deaths += 1
                continue
            
            for prey in self.prey_list[:]:
                if predator.position.distance_to(prey.position) < 8:
                    predator.eat_prey(prey)
                    self.prey_list.remove(prey)
                    self.total_prey_deaths += 1
                    break
            
            if predator.can_reproduce():
                for other in self.predator_list:
                    if other == predator:
                        continue
                    if (other.can_reproduce() and 
                        predator.position.distance_to(other.position) < 40):
                        baby = predator.reproduce()
                        other.reproduction_cooldown = PREDATOR_REPRODUCTION_COOLDOWN
                        self.predator_list.append(baby)
                        self.predator_births_this_frame += 1
                        self.total_predator_births += 1
                        break
    
    def spawn_food(self):
        self.food_spawn_timer += 1
        if (self.food_spawn_timer >= FOOD_SPAWN_INTERVAL and 
            len(self.food_list) < MAX_FOOD):
            self.food_list.append(
                Food(random.randint(20, WIDTH-20), 
                     random.randint(20, HEIGHT-20))
            )
            self.food_spawn_timer = 0
    
    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        for food in self.food_list:
            food.draw(self.screen)
        
        for prey in self.prey_list:
            prey.draw(self.screen)
        
        for predator in self.predator_list:
            predator.draw(self.screen)
        
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self): #desenez textul cu statistici si controale
        stats = [
            f"Prey: {len(self.prey_list)}",
            f"Predators: {len(self.predator_list)}",
            f"Food: {len(self.food_list)}",
            f"",
            f"Total Births:",
            f"  Prey: {self.total_prey_births}",
            f"  Pred: {self.total_predator_births}",
            f"",
            f"Total Deaths:",
            f"  Prey: {self.total_prey_deaths}",
            f"  Pred: {self.total_predator_deaths}",
        ]
        
        y = 10
        for stat in stats:
            text = self.font.render(stat, True, TEXT_COLOR)
            self.screen.blit(text, (10, y))
            y += 22
        
        controls = [
            "CONTROLS:",
            "SPACE - Pause/Resume",
            "R - Reset",
            "G - Show Graphs",
            "",
            "P - Add Prey",
            "O - Add Predator",
            "F - Add Food (+5)",
            "B - Add Obstacle (at mouse)",
            "C - Clear Obstacles"
        ]
        
        y = 10
        for control in controls:
            text = self.font.render(control, True, TEXT_COLOR)
            self.screen.blit(text, (WIDTH - 250, y))
            y += 22
        
        if self.paused:
            pause_text = self.big_font.render("  PAUSED", True, (255, 255, 0))
            rect = pause_text.get_rect(center=(WIDTH//2, 50))
            self.screen.blit(pause_text, rect)