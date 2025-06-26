"""
Barebones Desktop Pet Engine

A simple engine for managing virtual pets on the desktop.
"""

import time
import random
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET


class PetState(Enum):
    """States that a pet can be in."""
    IDLE = "idle"
    WALKING = "walking"
    SLEEPING = "sleeping"
    EATING = "eating"
    PLAYING = "playing"


class PetAssetManager:
    """
    Manages pet assets and animations.
    
    Attributes:
        pet_name: Name of the pet (e.g., "Patamon Shimeji")
        assets_path: Path to the pet's assets directory
        images_path: Path to the pet's sprite images
        conf_path: Path to the pet's configuration files
        sprites: Dictionary mapping sprite names to file paths
        animations: Dictionary mapping action names to animation sequences
    
    Methods:
        __init__(pet_name): Initialize asset manager for a specific pet
        _load_sprites(): Private method to load all PNG sprite files
        _load_animations(): Private method to parse actions.xml and load animations
        get_sprite_path(sprite_name): Get full file path for a sprite image
        get_animation(action_name): Get animation sequence for a specific action
        get_available_actions(): Get list of all available action names
    """
    
    def __init__(self, pet_name: str):
        self.pet_name = pet_name
        self.assets_path = Path(f"assets/pets/{pet_name}")
        character_name = pet_name.split()[0]  # "Patamon Shimeji" -> "Patamon"
        self.images_path = self.assets_path / "img" / character_name
        self.conf_path = self.assets_path / "conf"
        
        # Load sprites
        self.sprites: Dict[str, str] = {}
        self._load_sprites()
        
        # Load animations
        self.animations: Dict[str, List[Dict]] = {}
        self._load_animations()
    
    def _load_sprites(self):
        """Load all sprite images."""
        if self.images_path.exists():
            for file in self.images_path.glob("*.png"):
                sprite_name = file.stem  # e.g., "shime1", "shime2"
                self.sprites[sprite_name] = str(file)
    
    def _load_animations(self):
        """Load animations from actions.xml."""
        actions_file = self.conf_path / "actions.xml"
        if not actions_file.exists():
            return
            
        tree = ET.parse(actions_file)
        root = tree.getroot()
        
        # Define namespace
        namespace = {'mascot': 'http://www.group-finity.com/Mascot'}
        
        # Use namespace-aware findall
        for action in root.findall('.//mascot:Action', namespace):
            action_name = action.get("Name")
            if action_name:
                poses = []
                # Use namespace-aware findall for Animation and Pose
                for animation in action.findall('.//mascot:Animation', namespace):
                    for pose in animation.findall('.//mascot:Pose', namespace):
                        pose_data = {
                            "image": pose.get("Image", "").lstrip("/"),
                            "anchor": pose.get("ImageAnchor", "64,128"),
                            "velocity": pose.get("Velocity", "0,0"),
                            "duration": int(pose.get("Duration", "250"))
                        }
                        poses.append(pose_data)
                
                if poses:
                    self.animations[action_name] = poses
    
    def get_sprite_path(self, sprite_name: str) -> str | None:
        """Get the full path to a sprite image."""
        return self.sprites.get(sprite_name)
    
    def get_animation(self, action_name: str) -> List[Dict] | None:
        """Get animation sequence for an action."""
        return self.animations.get(action_name)
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions."""
        return list(self.animations.keys())


@dataclass
class Pet:
    """
    Represents a virtual pet.
    
    Attributes:
        name: Unique name identifier for the pet
        x: X-coordinate position on screen (default: 100)
        y: Y-coordinate position on screen (default: 100)
        state: Current behavioral state (IDLE, WALKING, SLEEPING, etc.)
        current_action: Current animation action being performed
        animation_frame: Current frame index in the animation sequence
        frame_timer: Timer for controlling frame advancement (in milliseconds)
    
    Methods:
        update(asset_manager, delta_time_ms): Update pet's animation and state
        _update_action_from_state(): Private method to map state to action
        get_current_sprite(asset_manager): Get current sprite file path for rendering
    """

    name: str
    x: int = 100
    y: int = 100
    state: PetState = PetState.IDLE
    current_action: str = "Stand"
    animation_frame: int = 0
    frame_timer: int = 0
    
    def update(self, asset_manager: PetAssetManager, delta_time_ms: int = 100):
        """Update pet's internal state and animation."""
        # Get current animation
        animation = asset_manager.get_animation(self.current_action)
        if animation and self.animation_frame < len(animation):
            pose = animation[self.animation_frame]
            
            # Update frame timer with actual elapsed time
            self.frame_timer += delta_time_ms
            if self.frame_timer >= pose["duration"]:
                self.frame_timer = 0
                self.animation_frame += 1
                
                # Loop animation
                if self.animation_frame >= len(animation):
                    self.animation_frame = 0
        
        # Removed random state changes - pet will stay in current state
        # unless manually changed via the GUI
    
    def _update_action_from_state(self):
        """Update action based on current state."""
        action_map = {
            PetState.IDLE: "Stand",
            PetState.WALKING: "Walk",
            PetState.SLEEPING: "Sprawl",
            PetState.EATING: "Sit",
            PetState.PLAYING: "SitAndDangleLegs"
        }
        self.current_action = action_map.get(self.state, "Stand")
        self.animation_frame = 0
        self.frame_timer = 0
    
    def get_current_sprite(self, asset_manager: PetAssetManager) -> str | None:
        """Get the current sprite path for rendering."""
        animation = asset_manager.get_animation(self.current_action)
        if animation and self.animation_frame < len(animation):
            pose = animation[self.animation_frame]
            sprite_name = pose["image"].replace(".png", "")
            return asset_manager.get_sprite_path(sprite_name)
        return None


class PetEngine:
    """
    Main engine for managing desktop pets.
    
    Attributes:
        pets: List of all active Pet instances
        asset_managers: Dictionary mapping pet types to their asset managers
        running: Boolean flag indicating if the engine is active
        screen_width: Width of the screen in pixels (default: 1920)
        screen_height: Height of the screen in pixels (default: 1080)
    
    Methods:
        __init__(): Initialize the pet engine
        add_pet(pet_name, pet_type): Create and add a new pet to the engine
        remove_pet(name): Remove a pet by its name, returns success status
        get_pet(name): Retrieve a pet instance by name
        update_pets(delta_time_ms): Update all pets' states and animations
        _move_pet(pet): Private method to handle pet movement logic
        start(): Start the main engine loop (blocking)
        stop(): Stop the engine and exit the main loop
        _display_status(): Private method to print status of all pets
        get_pet_sprite(pet): Get current sprite path for rendering a pet
    """
    
    def __init__(self):
        self.pets: List[Pet] = []
        self.asset_managers: Dict[str, PetAssetManager] = {}
        self.running = False
        self.screen_width = 1920
        self.screen_height = 1080
        
    def add_pet(self, pet_name: str, pet_type: str = "Patamon Shimeji") -> Pet:
        """Add a new pet to the engine."""
        pet = Pet(name=pet_name)
        self.pets.append(pet)
        
        # Load assets for this pet type
        if pet_type not in self.asset_managers:
            self.asset_managers[pet_type] = PetAssetManager(pet_type)
        
        return pet
    
    def remove_pet(self, name: str) -> bool:
        """Remove a pet by name."""
        for i, pet in enumerate(self.pets):
            if pet.name == name:
                del self.pets[i]
                return True
        return False
    
    def get_pet(self, name: str) -> Pet | None:
        """Get a pet by name."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None
    
    def update_pets(self, delta_time_ms: int = 1000):
        """Update all pets in the engine."""
        for pet in self.pets:
            # Use the first available asset manager for now
            asset_manager = next(iter(self.asset_managers.values()))
            pet.update(asset_manager, delta_time_ms)
            self._move_pet(pet)
    
    def _move_pet(self, pet: Pet):
        """Move a pet around the screen."""
        if pet.state == PetState.WALKING:
            # Simple random movement
            pet.x += random.randint(-10, 10)
            pet.y += random.randint(-10, 10)
            
            # Keep pet within screen bounds
            pet.x = max(0, min(self.screen_width, pet.x))
            pet.y = max(0, min(self.screen_height, pet.y))
    
    def start(self):
        """Start the pet engine."""
        self.running = True
        print("Pet engine started!")
        
        try:
            while self.running:
                self.update_pets()
                self._display_status()
                time.sleep(1)  # Update every second
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the pet engine."""
        self.running = False
        print("Pet engine stopped!")
    
    def _display_status(self):
        """Display current status of all pets."""
        if not self.pets:
            return
            
        print("\n" + "="*50)
        for pet in self.pets:
            print(f"{pet.name}: {pet.state.value} at ({pet.x}, {pet.y})")
        print("="*50)

    def get_pet_sprite(self, pet: Pet) -> str | None:
        """Get the current sprite path for a pet."""
        asset_manager = next(iter(self.asset_managers.values()))
        return pet.get_current_sprite(asset_manager)



