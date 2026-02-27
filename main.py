from simulation import Simulation

if __name__ == "__main__":
    print("=" * 50)
    print(" ADVANCED PREDATOR-PREY SIMULATION ")
    print("=" * 50)
    print("\nStarting simulation...")
    print("Press SPACE to pause, R to reset, G for graphs")
    print("\n" + "=" * 50 + "\n")
    
    sim = Simulation()
    sim.run()
    
    print("\n" + "=" * 50)
    print("Simulation ended. Thanks for watching!")
    print("=" * 50)
