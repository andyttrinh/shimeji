import tkinter as tk

class DesktopWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()

    def setup_window(self):
        self.root.title("Shimeji Desktop Pet")
        self.root.geometry("800x600")
        
        # Make window transparent
        self.root.attributes('-alpha', 0.9)
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        
        # macOS-specific: make window transparent/click-through
        self.root.attributes('-transparent', True)

        # Make window ignored by window manager (allows click-through)
        self.root.attributes('-type', 'dock')

    def run(self):
        self.root.mainloop()

