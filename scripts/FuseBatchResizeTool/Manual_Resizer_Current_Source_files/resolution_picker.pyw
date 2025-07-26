import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ResolutionPicker(tk.Toplevel):
    def __init__(self, parent, initial_format="BMP", initial_bit_depth=24, format_options=None):
        super().__init__(parent)
        self.withdraw() # Withdraw immediately
        self.title("Output Settings")
        
        # Set window size and position - make it narrower for better proportions
        self.geometry("350x500")
        self.resizable(True, True)
        self.minsize(350, 400)

        # File format configuration
        if format_options is None:
            self.format_options = {
                "BMP": [1, 4, 8, 16, 24, 32],
                "PNG": [8, 16, 24, 32],
                "JPG": [8, 16, 24],
                "JPEG": [8, 16, 24]
            }
        else:
            self.format_options = format_options
        
        self.selected_format = tk.StringVar(value=initial_format)
        self.selected_bit_depth = tk.IntVar(value=initial_bit_depth)

        # Default resolutions
        self.default_resolutions = [
            "200x200",
            "150x150",
            "100x100",
            "50x50"
        ]

        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top title
        ttk.Label(main_frame, text="Output Settings", font=("Arial", 16, "bold")).pack(side=tk.TOP, pady=(0, 10))

        # Create horizontal split frame
        split_frame = ttk.Frame(main_frame)
        split_frame.pack(fill=tk.BOTH, expand=True)

        # LEFT SIDE - Resolutions (keep all existing functionality)
        left_frame = ttk.Frame(split_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # Create and pack the resolution list frame
        list_frame = ttk.LabelFrame(left_frame, text="Available Resolutions", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create listbox and scrollbar
        self.listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, 
                                 activestyle='none',  # No underline on active item
                                 selectbackground='#0078D7',  # Windows blue selection color
                                 selectforeground='white')
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Pack listbox and scrollbar
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind Ctrl+A to select all
        self.listbox.bind('<Control-a>', self.select_all)
        self.bind('<Control-a>', self.select_all)  # Also bind to window

        # Create custom resolution frame
        custom_frame = ttk.LabelFrame(left_frame, text="Add Custom Resolution", padding="5")
        custom_frame.pack(fill=tk.X, pady=(0, 10))

        # Add validation for numeric input
        vcmd = (self.register(self.validate_number), '%P')

        # Width entry
        width_frame = ttk.Frame(custom_frame)
        width_frame.pack(fill=tk.X, pady=2)
        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT)
        self.width_entry = ttk.Entry(width_frame, width=6, validate='key', validatecommand=vcmd)
        self.width_entry.pack(side=tk.LEFT, padx=5)

        # Height entry
        height_frame = ttk.Frame(custom_frame)
        height_frame.pack(fill=tk.X, pady=2)
        ttk.Label(height_frame, text="Height:").pack(side=tk.LEFT)
        self.height_entry = ttk.Entry(height_frame, width=6, validate='key', validatecommand=vcmd)
        self.height_entry.pack(side=tk.LEFT, padx=5)

        # Add resolution button
        ttk.Button(custom_frame, text="Add Resolution", command=self.add_resolution).pack(fill=tk.X, pady=(5, 0))

        # Resolution management buttons
        resolution_buttons_frame = ttk.Frame(left_frame)
        resolution_buttons_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(resolution_buttons_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(resolution_buttons_frame, text="Select All", command=lambda: self.select_all(None)).pack(side=tk.LEFT, padx=5)

        # Add horizontal separator between resolution buttons and main buttons
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # RIGHT SIDE - File Format and Bit Depth
        right_frame = ttk.Frame(split_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 0))

        # File Format selection
        format_frame = ttk.LabelFrame(right_frame, text="File Format", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        for format_name in self.format_options.keys():
            ttk.Radiobutton(format_frame, text=format_name, variable=self.selected_format, 
                          value=format_name, command=self._on_format_change).pack(anchor=tk.W, pady=2)

        # Bit Depth selection
        bit_depth_frame = ttk.LabelFrame(right_frame, text="Bit Depth", padding="10")
        bit_depth_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.bit_radio_buttons = []
        self._bit_depth_frame = bit_depth_frame
        self._on_format_change()  # Initialize bit depth options

        # Main button frame (Confirm/Cancel)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Create a frame for both buttons to center them together
        center_frame = ttk.Frame(button_frame)
        center_frame.pack(expand=True)

        # Add buttons - Confirm and Cancel next to each other in the center with divider
        ttk.Button(center_frame, text="Confirm", command=self.confirm).pack(side=tk.LEFT, padx=5)
        ttk.Separator(center_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(center_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

        # Right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        self.listbox.bind("<Button-3>", self.show_context_menu)

        # Load saved resolutions or defaults
        self.load_resolutions()
        
        # Ensure the config file is valid
        self.repair_resolution_config()

        # Store the result
        self.result = None

    def _on_format_change(self):
        """Update bit depth options when format changes"""
        # Clear existing bit depth radio buttons
        for btn in self.bit_radio_buttons:
            btn.destroy()
        self.bit_radio_buttons = []
        
        # Get available bit depths for selected format
        selected_format = self.selected_format.get()
        available_depths = self.format_options[selected_format]
        
        # Create new radio buttons for available bit depths
        for depth in available_depths:
            btn = ttk.Radiobutton(self._bit_depth_frame, text=f"{depth}-bit", 
                                variable=self.selected_bit_depth, value=depth)
            btn.pack(anchor=tk.W, pady=2)
            self.bit_radio_buttons.append(btn)
        
        # Set to highest available depth if current selection is not valid
        if self.selected_bit_depth.get() not in available_depths:
            self.selected_bit_depth.set(available_depths[-1])

    def validate_number(self, value):
        if value == "":
            return True
        try:
            num = int(value)
            return 0 <= num <= 9999
        except ValueError:
            return False

    def add_resolution(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            
            if width <= 0 or height <= 0:
                messagebox.showerror("Error", "Width and height must be greater than 0")
                return
                
            resolution = f"{width}x{height}"
            
            # Check if resolution already exists
            if resolution not in self.listbox.get(0, tk.END):
                # Store current selections
                current_selections = list(self.listbox.curselection())
                
                # Add new resolution
                self.listbox.insert(tk.END, resolution)
                
                # Restore previous selections
                for index in current_selections:
                    self.listbox.selection_set(index)
                    
                # Select the new resolution
                self.listbox.selection_set(tk.END)
                
                # Clear entries
                self.width_entry.delete(0, tk.END)
                self.height_entry.delete(0, tk.END)
                
                # Save resolutions
                self.save_resolutions()
            else:
                messagebox.showwarning("Warning", "This resolution already exists")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def delete_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            return
            
        # Delete in reverse order to maintain correct indices
        for index in reversed(selected):
            self.listbox.delete(index)
            
        # Save the updated list
        self.save_resolutions()

    def show_context_menu(self, event):
        # Only show menu if clicking on an item
        index = self.listbox.nearest(event.y)
        if index >= 0 and self.listbox.bbox(index):  # Check if item exists and is visible
            # Select the item under the cursor if not already selected
            if index not in self.listbox.curselection():
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(index)
            
            # Show the menu at mouse position
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
        return "break"  # Prevent default right-click behavior

    def load_resolutions(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), "resolution_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    resolutions = json.load(f)
                    if resolutions and isinstance(resolutions, list) and len(resolutions) > 0:
                        for res in resolutions:
                            # Validate resolution format
                            if isinstance(res, str) and 'x' in res:
                                try:
                                    width, height = map(int, res.split('x'))
                                    if width > 0 and height > 0:
                                        self.listbox.insert(tk.END, res)
                                    else:
                                        print(f"Invalid resolution dimensions: {res}")
                                except ValueError:
                                    print(f"Invalid resolution format: {res}")
                            else:
                                print(f"Invalid resolution entry: {res}")
                        # If we successfully loaded at least one resolution, return
                        if self.listbox.size() > 0:
                            return
        except Exception as e:
            print(f"Error loading resolutions: {e}")
            
        # If no saved resolutions or error, load defaults
        print("Loading default resolutions...")
        for res in self.default_resolutions:
            self.listbox.insert(tk.END, res)

    def save_resolutions(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), "resolution_config.json")
            resolutions = list(self.listbox.get(0, tk.END))
            with open(config_path, 'w') as f:
                json.dump(resolutions, f)
        except Exception as e:
            print(f"Error saving resolutions: {e}")

    def repair_resolution_config(self):
        """Repair the resolution config file if it's corrupted."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "resolution_config.json")
            
            # If the file doesn't exist or is corrupted, recreate it with defaults
            if not os.path.exists(config_path):
                print("Resolution config file not found. Creating with defaults...")
                with open(config_path, 'w') as f:
                    json.dump(self.default_resolutions, f)
                return True
            
            # Try to read and validate the existing file
            try:
                with open(config_path, 'r') as f:
                    resolutions = json.load(f)
                
                # Check if the file is valid
                if not isinstance(resolutions, list) or len(resolutions) == 0:
                    print("Resolution config file is invalid. Recreating with defaults...")
                    with open(config_path, 'w') as f:
                        json.dump(self.default_resolutions, f)
                    return True
                
                # Validate each resolution
                valid_resolutions = []
                for res in resolutions:
                    if isinstance(res, str) and 'x' in res:
                        try:
                            width, height = map(int, res.split('x'))
                            if width > 0 and height > 0:
                                valid_resolutions.append(res)
                        except ValueError:
                            print(f"Skipping invalid resolution: {res}")
                
                # If no valid resolutions, use defaults
                if not valid_resolutions:
                    print("No valid resolutions found. Using defaults...")
                    with open(config_path, 'w') as f:
                        json.dump(self.default_resolutions, f)
                    return True
                
                # If we have valid resolutions, save them back (cleaned)
                if len(valid_resolutions) != len(resolutions):
                    print("Some resolutions were invalid. Saving cleaned list...")
                    with open(config_path, 'w') as f:
                        json.dump(valid_resolutions, f)
                
                return True
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading resolution config: {e}. Recreating with defaults...")
                with open(config_path, 'w') as f:
                    json.dump(self.default_resolutions, f)
                return True
                
        except Exception as e:
            print(f"Error repairing resolution config: {e}")
            return False

    def confirm(self):
        selected = self.listbox.curselection()
        if not selected:
            # If no resolutions are selected, automatically select all available ones
            all_items = self.listbox.get(0, tk.END)
            if all_items:
                # Select all items
                self.listbox.select_set(0, tk.END)
                selected = self.listbox.curselection()
                messagebox.showinfo("Auto-Selection", "No resolutions were selected. All available resolutions have been automatically selected.")
            else:
                # If there are no resolutions at all, add default ones and select them
                for res in self.default_resolutions:
                    self.listbox.insert(tk.END, res)
                self.listbox.select_set(0, tk.END)
                selected = self.listbox.curselection()
                messagebox.showinfo("Default Resolutions", "No resolutions were available. Default resolutions have been added and selected.")
        
        # Get resolutions
        resolutions = []
        for index in selected:
            resolution = self.listbox.get(index)
            width, height = map(int, resolution.split('x'))
            resolutions.append((width, height))
        
        # Get format settings
        selected_format = self.selected_format.get()
        selected_bit_depth = self.selected_bit_depth.get()
        
        # Return tuple: (resolutions, format, bit_depth)
        self.result = (resolutions, selected_format, selected_bit_depth)
        
        self.save_resolutions()
        self.destroy()

    def select_all(self, event):
        self.listbox.select_set(0, tk.END)
        return "break"  # Prevent default Ctrl+A behavior
