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
        self.root.geometry("800x600")
        
        # Make window transparent
        self.root.attributes('-alpha', 0.1)
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # macOS-specific: make window transparent
        self.root.attributes('-transparent', True)
        
        # Create canvas for pets
        self.canvas = tk.Canvas(self.root, bg='systemTransparent', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Add a simple test rectangle
        self.test_pet = self.canvas.create_rectangle(100, 100, 150, 150, fill='red', outline='white')
        
        # Force window creation
        self.root.update_idletasks()

    def setup_macos_clickthrough(self):
        try:
            from AppKit import NSApplication
            
            # Get the native window
            NSApp = NSApplication.sharedApplication()
            
            # Find our tkinter window
            for window in NSApp.windows():
                if hasattr(window, 'frame') and window.frame().size.width == 800:
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

    def run(self):
        self.root.mainloop()

