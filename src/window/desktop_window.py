import tkinter as tk
import sys

class DesktopWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        if sys.platform == "darwin":
            self.setup_macos_clickthrough()

    def setup_window(self):
        self.root.title("Shimeji Desktop Pet")
        
        # Get screen dimensions first
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Make window full screen
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")  # Set explicit size and position
        self.root.attributes('-fullscreen', True)  # Full screen on macOS
        
        # Make window transparent
        self.root.attributes('-alpha', 0.8)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparent', True)
        
        # Create canvas for pets (will fill entire window)
        self.canvas = tk.Canvas(self.root, bg='systemTransparent', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Force window creation first
        self.root.update_idletasks()
        
        # Add window outline for reference
        self.canvas.create_rectangle(0, 0, screen_width, screen_height, 
                                    outline='blue', width=3)
        
        # Add a simple test rectangle
        self.test_pet = self.canvas.create_rectangle(100, 100, 150, 150, fill='red', outline='white')

    def setup_macos_clickthrough(self):
        try:
            from AppKit import NSApplication
            
            # Get the native window
            NSApp = NSApplication.sharedApplication()
            
            # Get our window's actual dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Find our tkinter window by matching its full-screen dimensions
            for window in NSApp.windows():
                if hasattr(window, 'frame'):
                    frame = window.frame()
                    if (frame.size.width == screen_width and 
                        frame.size.height == screen_height):
                        # Make it ignore mouse events (click-through)
                        window.setIgnoresMouseEvents_(True)
                        # Keep it floating on top (25 is the floating level constant)
                        window.setLevel_(25)
                        print("macOS click-through enabled!")
                        break
        except ImportError:
            print("PyObjC not installed. Install with: pip install pyobjc-framework-Cocoa")
        except Exception as e:
            print(f"Click-through setup failed: {e}")

    def move_square(self):
        """Move the test square in a simple pattern"""
        # Get current position
        coords = self.canvas.coords(self.test_pet)
        x1, y1, x2, y2 = coords
        
        # Simple movement: move right by 5 pixels, wrap around when hitting screen edge
        new_x1 = (x1 + 5) % self.root.winfo_screenwidth()
        new_x2 = (x2 + 5) % self.root.winfo_screenwidth()
        
        # Move the square
        self.canvas.coords(self.test_pet, new_x1, y1, new_x2, y2)
        
        # Schedule the next movement (every 100ms = 10 FPS)
        self.root.after(100, self.move_square)

    def run(self):
        # Start the movement
        self.move_square()
        self.root.mainloop()

