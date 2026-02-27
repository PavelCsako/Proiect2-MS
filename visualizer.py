import matplotlib.pyplot as plt

class SimulationVisualizer:
    
    def __init__(self):
        self.history = {
            'time': [],
            'prey_count': [],
            'predator_count': [],
            'food_count': [],
            'prey_births': [],
            'predator_births': [],
            'prey_avg_energy': [],
            'predator_avg_energy': []
        }
        #dictionar cu liste goale

        self.frame_count = 0 #counter de frame uri
        self.fig = None
        self.axes = None
        self.running = False #flag pt starea vizualizatorului
        
    #la fiecare frame, actualizez istoricul cu datele curente
    def update_history(self, prey_list, predator_list, food_list, 
                      prey_births, predator_births):
        self.frame_count += 1
        self.history['time'].append(self.frame_count)
        self.history['prey_count'].append(len(prey_list))
        self.history['predator_count'].append(len(predator_list))
        self.history['food_count'].append(len(food_list))
        self.history['prey_births'].append(prey_births)
        self.history['predator_births'].append(predator_births)
        
        #calculez energia medie pentru prey si predatori
        if prey_list:
            avg_prey_energy = sum(p.energy for p in prey_list) / len(prey_list)
            self.history['prey_avg_energy'].append(avg_prey_energy)
        else:
            self.history['prey_avg_energy'].append(0)
        
        if predator_list:
            avg_pred_energy = sum(p.energy for p in predator_list) / len(predator_list)
            self.history['predator_avg_energy'].append(avg_pred_energy)
        else:
            self.history['predator_avg_energy'].append(0)
    
    def plot_graphs(self):
        if not self.history['time']:
            print("Nu exista date pentru grafice!")
            return
        
        # Creez figura cu 4 subgrafice
        self.fig, self.axes = plt.subplots(2, 2, figsize=(14, 10))
        self.fig.suptitle('Predator-Prey Simulation Statistics', 
                         fontsize=16, fontweight='bold')
        
        time = self.history['time']
        
        # Populatie
        ax1 = self.axes[0, 0]
        ax1.plot(time, self.history['prey_count'], 
                color='green', linewidth=2, label='Prey')
        ax1.plot(time, self.history['predator_count'], 
                color='red', linewidth=2, label='Predators')
        ax1.plot(time, self.history['food_count'], 
                color='gold', linewidth=1, linestyle='--', label='Food')
        ax1.set_xlabel('Time (frames)')
        ax1.set_ylabel('Population')
        ax1.set_title('Population Over Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Birth Rates
        ax2 = self.axes[0, 1]
        ax2.plot(time, self.history['prey_births'], 
                color='lightgreen', linewidth=2, label='Prey Births')
        ax2.plot(time, self.history['predator_births'], 
                color='salmon', linewidth=2, label='Predator Births')
        ax2.set_xlabel('Time (frames)')
        ax2.set_ylabel('Births per Frame')
        ax2.set_title('Birth Rates Over Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Average Energy
        ax3 = self.axes[1, 0]
        ax3.plot(time, self.history['prey_avg_energy'], 
                color='green', linewidth=2, label='Prey Avg Energy')
        ax3.plot(time, self.history['predator_avg_energy'], 
                color='red', linewidth=2, label='Predator Avg Energy')
        ax3.set_xlabel('Time (frames)')
        ax3.set_ylabel('Average Energy')
        ax3.set_title('Average Energy Levels')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Ratio Predator/Prey
        ax4 = self.axes[1, 1]
        ratios = []
        for i in range(len(time)):
            prey_c = self.history['prey_count'][i]
            pred_c = self.history['predator_count'][i]
            if prey_c > 0:
                ratios.append(pred_c / prey_c)
            else:
                ratios.append(0)
        
        ax4.plot(time, ratios, color='purple', linewidth=2)
        ax4.axhline(y=0.20, color='orange', linestyle='--', 
                   label='Target Ratio (0.20)')
        ax4.set_xlabel('Time (frames)')
        ax4.set_ylabel('Predator/Prey Ratio')
        ax4.set_title('Predator to Prey Ratio')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def save_data(self, filename='simulation_data.csv'):
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Time', 'Prey', 'Predators', 'Food', 
                           'Prey_Births', 'Predator_Births',
                           'Prey_Avg_Energy', 'Predator_Avg_Energy'])
            
            # Date
            for i in range(len(self.history['time'])):
                writer.writerow([
                    self.history['time'][i],
                    self.history['prey_count'][i],
                    self.history['predator_count'][i],
                    self.history['food_count'][i],
                    self.history['prey_births'][i],
                    self.history['predator_births'][i],
                    self.history['prey_avg_energy'][i],
                    self.history['predator_avg_energy'][i]
                ])
        
        print(f"Date salvate în {filename}")