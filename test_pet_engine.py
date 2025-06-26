"""
Simple test for PetEngine with basic GUI display
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from pathlib import Path
from PIL import Image, ImageTk
from src.core.pet_engine import PetEngine, PetState

class PetEngineGUI:
    """Simple GUI to test the PetEngine with visual display."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pet Engine Test")
        self.root.geometry("800x600")
        
        # Create engine
        self.engine = PetEngine()
        self.engine.screen_width = 800
        self.engine.screen_height = 600
        
        # Add pets for both types
        self.patamon_pet = self.engine.add_pet("PatamonTest", "Patamon Shimeji")
        self.charmander_pet = self.engine.add_pet("CharmanderTest", "Charmander Shimeji")
        
        # Start with Patamon
        self.current_pet = self.patamon_pet
        
        # Debug assets
        self.debug_assets()
        
        # GUI elements
        self.setup_gui()
        
        # Animation variables
        self.current_image = None
        self.running = False
        
    def setup_gui(self):
        """Setup the GUI elements."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Canvas for displaying the pet
        self.canvas = tk.Canvas(main_frame, width=600, height=400, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Control buttons
        ttk.Button(main_frame, text="Start", command=self.start_animation).grid(row=1, column=0, pady=5)
        ttk.Button(main_frame, text="Stop", command=self.stop_animation).grid(row=1, column=1, pady=5)
        
        # Pet selector
        ttk.Label(main_frame, text="Select Pet:").grid(row=1, column=2, pady=5)
        self.pet_var = tk.StringVar(value="Patamon")
        pet_combo = ttk.Combobox(main_frame, textvariable=self.pet_var, 
                                values=["Patamon", "Charmander"])
        pet_combo.grid(row=1, column=3, pady=5)
        pet_combo.bind("<<ComboboxSelected>>", self.change_pet)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Pet info label
        self.pet_info_label = ttk.Label(main_frame, text="")
        self.pet_info_label.grid(row=3, column=0, columnspan=4, pady=5)
        
        # Action selector
        ttk.Label(main_frame, text="Change Action:").grid(row=4, column=0, pady=5)
        self.action_var = tk.StringVar(value="Stand")
        
        # Create action combo first
        self.action_combo = ttk.Combobox(main_frame, textvariable=self.action_var, 
                                        values=[])
        self.action_combo.grid(row=4, column=1, pady=5)
        self.action_combo.bind("<<ComboboxSelected>>", self.change_action)
        
        # Now update the action list after action_combo is created
        self.update_action_list()
        
    def load_and_display_image(self, image_path):
        """Load and display an image on the canvas."""
        try:
            if image_path and Path(image_path).exists():
                print(f"Loading image: {image_path}")
                
                # Load image with PIL
                image = Image.open(image_path)
                print(f"Image loaded, size: {image.size}, mode: {image.mode}")
                
                # Convert to RGB if necessary (in case of RGBA or other formats)
                if image.mode != 'RGB':
                    print(f"Converting from {image.mode} to RGB")
                    image = image.convert('RGB')
                
                # Resize if too large (optional)
                if image.width > 200 or image.height > 200:
                    print(f"Resizing from {image.size} to max 200x200")
                    image.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                print(f"Creating PhotoImage from {image.size} image")
                
                # Workaround: Save to temporary file and load with tkinter
                import tempfile
                import os
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    image.save(tmp_file.name, format='PNG')
                    tmp_path = tmp_file.name
                
                try:
                    # Load with tkinter's PhotoImage
                    photo = tk.PhotoImage(file=tmp_path)
                    
                    # Clear canvas and display new image
                    self.canvas.delete("all")
                    self.canvas.create_image(300, 200, image=photo, anchor="center")
                    
                    # Keep a reference to prevent garbage collection
                    self.current_image = photo
                    
                    print("Image displayed successfully")
                    return True
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                        
            else:
                # Display a placeholder if image not found
                self.canvas.delete("all")
                self.canvas.create_text(300, 200, text="Image not found", fill="red", font=("Arial", 16))
                return False
        except Exception as e:
            print(f"Error loading image: {e}")
            print(f"Image path: {image_path}")
            import traceback
            traceback.print_exc()  # Print full stack trace
            self.canvas.delete("all")
            self.canvas.create_text(300, 200, text=f"Error: {e}", fill="red", font=("Arial", 12))
            return False
    
    def update_display(self):
        """Update the display with current pet state."""
        if not self.running:
            return
            
        # Update current pet with actual time delta
        asset_manager = self.get_current_asset_manager()
        self.current_pet.update(asset_manager, 100)
        
        # Get current sprite
        sprite_path = self.current_pet.get_current_sprite(asset_manager)
        
        # Debug: Print sprite path and asset info
        print(f"Debug - Sprite path: {sprite_path}")
        print(f"Debug - Pet action: {self.current_pet.current_action}")
        print(f"Debug - Animation frame: {self.current_pet.animation_frame}")
        
        # Check asset manager
        print(f"Debug - Available sprites: {list(asset_manager.sprites.keys())[:5]}...")
        print(f"Debug - Available actions: {list(asset_manager.animations.keys())[:5]}...")
        
        # Display image
        if sprite_path:
            self.load_and_display_image(sprite_path)
        else:
            print("Debug - No sprite path returned!")
        
        # Update status
        pet_name = "Patamon" if self.current_pet == self.patamon_pet else "Charmander"
        self.status_label.config(text=f"{pet_name}: {self.current_pet.current_action}")
        self.pet_info_label.config(text=f"Position: ({self.current_pet.x}, {self.current_pet.y}) | Frame: {self.current_pet.animation_frame}")
        
        # Schedule next update
        if self.running:
            self.root.after(100, self.update_display)  # Update every 100ms
    
    def start_animation(self):
        """Start the animation loop."""
        self.running = True
        self.status_label.config(text="Animation running...")
        self.update_display()
    
    def stop_animation(self):
        """Stop the animation loop."""
        self.running = False
        self.status_label.config(text="Animation stopped")
    
    def change_pet(self, event=None):
        """Change the current pet being displayed."""
        pet_name = self.pet_var.get()
        if pet_name == "Patamon":
            self.current_pet = self.patamon_pet
        else:
            self.current_pet = self.charmander_pet
        
        # Update action list for the new pet
        self.update_action_list()
        
        # Reset action to first available one
        asset_manager = self.get_current_asset_manager()
        available_actions = asset_manager.get_available_actions()
        if available_actions:
            self.action_var.set(available_actions[0])
            self.current_pet.current_action = available_actions[0]
            self.current_pet.animation_frame = 0
            self.current_pet.frame_timer = 0
        
        self.status_label.config(text=f"Switched to {pet_name}")
    
    def update_action_list(self):
        """Update the action dropdown with current pet's available actions."""
        asset_manager = self.get_current_asset_manager()
        available_actions = asset_manager.get_available_actions()
        self.action_combo['values'] = available_actions
        if available_actions and self.action_var.get() not in available_actions:
            self.action_var.set(available_actions[0])
    
    def get_current_asset_manager(self):
        """Get the asset manager for the current pet."""
        pet_type = "Patamon Shimeji" if self.current_pet == self.patamon_pet else "Charmander Shimeji"
        return self.engine.asset_managers[pet_type]
    
    def change_action(self, event=None):
        """Change the pet's action directly."""
        new_action = self.action_var.get()
        self.current_pet.current_action = new_action
        self.current_pet.animation_frame = 0
        self.current_pet.frame_timer = 0
        self.status_label.config(text=f"Action changed to: {new_action}")
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

    def debug_assets(self):
        """Debug asset loading."""
        asset_manager = next(iter(self.engine.asset_managers.values()))
        print(f"Assets path: {asset_manager.assets_path}")
        print(f"Images path: {asset_manager.images_path}")
        print(f"Conf path: {asset_manager.conf_path}")
        print(f"Images path exists: {asset_manager.images_path.exists()}")
        print(f"Loaded sprites: {len(asset_manager.sprites)}")
        print(f"Loaded animations: {len(asset_manager.animations)}")
        
        if asset_manager.sprites:
            print(f"First few sprites: {list(asset_manager.sprites.items())[:3]}")
        if asset_manager.animations:
            print(f"First few actions: {list(asset_manager.animations.keys())[:3]}")

def main():
    """Main test function."""
    print("Starting Pet Engine GUI Test...")
    print("This will display a simple GUI with the pet animation.")
    
    # Create and run GUI
    gui = PetEngineGUI()
    gui.run()

if __name__ == "__main__":
    main() 