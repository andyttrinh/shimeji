from src.core.pet_engine import PetEngine

def main():
    """Simple demo of the pet engine."""
    engine = PetEngine()
    
    # Add a pet (will automatically load Patamon assets)
    pet = engine.add_pet("Fluffy", "Patamon Shimeji")
    
    print("Starting pet engine demo...")
    print("Press Ctrl+C to stop")
    
    engine.start()

if __name__ == "__main__":
    main()
