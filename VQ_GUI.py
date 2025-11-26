import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk, ImageDraw
import os

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, radius=20, bg="#4a6fc7", fg="white", 
                 font=("Arial", 10, "bold"), width=120, height=35, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent.cget('bg'))
        self.command = command
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.font = font
        self.width = width
        self.height = height
        self.text = text
        

        # binding of events like clicking on a button and hover effects
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self.draw_button()
        
    def draw_button(self, hover=False):
        self.delete("all")
        color = self.bg
        if hover:
            # Lighten color on hover
            r, g, b = int(self.bg[1:3], 16), int(self.bg[3:5], 16), int(self.bg[5:7], 16)
            r = min(255, int(r * 1.2))
            g = min(255, int(g * 1.2))
            b = min(255, int(b * 1.2))
            color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Draw rounded rectangle
        self.create_rounded_rectangle(0, 0, self.width, self.height, radius=self.radius, fill=color, outline="")
        
        # Add text
        self.create_text(self.width//2, self.height//2, text=self.text, fill=self.fg, font=self.font)
    
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_click(self, event):
        self.command()
    
    def _on_enter(self, event):
        self.draw_button(hover=True)
    
    def _on_leave(self, event):
        self.draw_button(hover=False)

class RoundedFrame(tk.Frame):
    def __init__(self, parent, radius=25, bg="#ffffff", **kwargs):
        super().__init__(parent, **kwargs)
        self.radius = radius
        self.bg = bg
        self.canvas = tk.Canvas(self, bg=parent.cget('bg'), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
    def draw_rounded_rect(self):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width > 1 and height > 1:
            points = [self.radius, 0,
                     width-self.radius, 0,
                     width, 0,
                     width, self.radius,
                     width, height-self.radius,
                     width, height,
                     width-self.radius, height,
                     self.radius, height,
                     0, height,
                     0, height-self.radius,
                     0, self.radius,
                     0, 0]
            self.canvas.create_polygon(points, smooth=True, fill=self.bg, outline="")

class VQ_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vector Quantization System")
        self.root.state("zoomed")  # Fullscreen / maximize
        
        # Blue/Violet color palette
        self.bg_color = "#1e2a4a"  # Dark blue background
        self.primary_color = "#8a2be2"  # Blue violet
        self.secondary_color = "#4a6fc7"  # Royal blue
        self.accent_color = "#ff6b6b"  # Coral accent for reset
        self.text_color = "#e6e6ff"  # Light lavender text
        self.frame_bg = "#2d3b5e"  # Medium blue frames
        self.button_color = "#6a5acd"  # Slate blue for buttons
        self.placeholder_bg = "#3a4a6b"  # Dark blue for placeholders
        
        self.root.configure(bg=self.bg_color)
        
        # Store images
        self.original_img = None
        self.decompressed_img = None
        self.original_panel = None
        self.decompressed_panel = None
        self.current_image_path = None


        # Title
        header_frame = tk.Frame(root, bg=self.primary_color, height=60)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="Vector Quantization System", 
            font=("Arial", 20, "bold"), 
            fg="white", 
            bg=self.primary_color,
            pady=20
        )
        title_label.pack()

        # frame for file selection and buttons
        top_frame = tk.Frame(root, bg=self.bg_color, pady=15)
        top_frame.pack(fill="x", padx=20)

        # File selection frame
        file_frame = tk.Frame(top_frame, bg=self.bg_color)
        file_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            file_frame, 
            text="Image Path:", 
            font=("Arial", 12, "bold"), 
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side="left")

        self.path_entry = tk.Entry(
            file_frame, 
            width=60, 
            font=("Arial", 12),
            relief="flat",
            bd=2,
            bg="#f0f0f5",
            fg="#333333"
        )
        self.path_entry.pack(side="left", padx=10)

        # Use rounded button for browse
        RoundedButton(
            file_frame, 
            text="Browse", 
            command=self.browse, 
            bg=self.button_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=100,
            height=35
        ).pack(side="left")

        # Buttons row
        button_frame = tk.Frame(top_frame, bg=self.bg_color)
        button_frame.pack(fill="x", pady=10)

        # Create rounded buttons
        RoundedButton(
            button_frame, 
            text="Compress", 
            command=self.open_compress_window,
            bg=self.button_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=120,
            height=40
        ).pack(side="left", padx=8)

        RoundedButton(
            button_frame, 
            text="Decompress", 
            command=self.open_decompress_window,  # Changed to open popup
            bg=self.button_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=120,
            height=40
        ).pack(side="left", padx=8)

        RoundedButton(
            button_frame, 
            text="Show Codebook / Binary", 
            command=self.show_files,
            bg=self.button_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=160,
            height=40
        ).pack(side="left", padx=8)

        RoundedButton(
            button_frame, 
            text="Reset", 
            command=self.reset_images,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=100,
            height=40
        ).pack(side="left", padx=8)

        
        # Image Display Frames
        main_frame = tk.Frame(root, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, pady=10, padx=20)

        # Left frame → Original image
        self.original_frame = tk.LabelFrame(
            main_frame, 
            text="Original Image", 
            font=("Arial", 14, "bold"), 
            padx=10, 
            pady=10,
            bg=self.frame_bg,
            fg=self.text_color,
            relief="flat",
            bd=0
        )
        self.original_frame.pack(side="left", expand=True, fill="both", padx=10)

        # Right frame → Decompressed image
        self.decompressed_frame = tk.LabelFrame(
            main_frame, 
            text="Decompressed Image", 
            font=("Arial", 14, "bold"), 
            padx=10, 
            pady=10,
            bg=self.frame_bg,
            fg=self.text_color,
            relief="flat",
            bd=0
        )
        self.decompressed_frame.pack(side="right", expand=True, fill="both", padx=10)

        # Create rounded placeholder frames
        self.original_placeholder = self.create_rounded_placeholder(self.original_frame, "No image loaded")
        self.decompressed_placeholder = self.create_rounded_placeholder(self.decompressed_frame, "Decompressed image will appear here")

    def create_rounded_placeholder(self, parent, text):
        # Create a canvas for rounded placeholder
        canvas = tk.Canvas(parent, bg=self.frame_bg, highlightthickness=0, width=400, height=400)
        canvas.pack(expand=True)
        
        # Draw rounded rectangle
        self.draw_rounded_rect(canvas, 400, 400, 25, self.placeholder_bg)
        
        # Add text
        canvas.create_text(200, 200, text=text, fill=self.text_color, font=("Arial", 12), width=350)
        
        return canvas

    def draw_rounded_rect(self, canvas, width, height, radius, color):
        # Create points for rounded rectangle
        points = [radius, 0,
                 width-radius, 0,
                 width, 0,
                 width, radius,
                 width, height-radius,
                 width, height,
                 width-radius, height,
                 radius, height,
                 0, height,
                 0, height-radius,
                 0, radius,
                 0, 0]
        canvas.create_polygon(points, smooth=True, fill=color, outline="")

    
    # File browsing
    def browse(self):
        file = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file)
            self.current_image_path = file
            self.show_original_image(file)

    def show_styled_error(self, title, message):
        """Show an error message with custom styling that matches our design"""
        error_popup = Toplevel(self.root)
        error_popup.title(title)
        error_popup.geometry("400x200")
        error_popup.configure(bg=self.bg_color)
        error_popup.resizable(False, False)
        
        # Center the popup
        error_popup.transient(self.root)
        error_popup.grab_set()
        
        # Position in center of parent window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (150 // 2)
        error_popup.geometry(f"+{x}+{y}")

        # Error icon and message
        tk.Label(
            error_popup, 
            text="⚠️",  # Error icon
            font=("Arial", 24),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(20, 10))

        tk.Label(
            error_popup, 
            text=message, 
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.text_color,
            wraplength=350
        ).pack(pady=(0, 20))

        # OK button 
        RoundedButton(
            error_popup, 
            text="OK", 
            command=error_popup.destroy,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=100,
            height=35
        ).pack(pady=10)

    def show_original_image(self, path):
        img = Image.open(path)
        
        # Set maximum dimensions (you can adjust these)
        max_width = 500
        max_height = 500
        
        # Calculate scaling factor while maintaining aspect ratio
        img_ratio = img.width / img.height
        
        if img.width > max_width or img.height > max_height:
            if img_ratio > 1:
                # Landscape image
                new_width = max_width
                new_height = int(max_width / img_ratio)
            else:
                # Portrait image
                new_height = max_height
                new_width = int(max_height * img_ratio)
            
            # Resize with high-quality filter
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create rounded image
        rounded_img = self.create_rounded_image(img, 25)
        self.original_img = ImageTk.PhotoImage(rounded_img)

        if self.original_panel:
            self.original_panel.config(image=self.original_img)
        else:
            self.original_panel = tk.Label(self.original_frame, image=self.original_img, bg=self.frame_bg)
            self.original_panel.pack(expand=True)
            
        # Remove placeholder if visible
        if self.original_placeholder.winfo_viewable():
            self.original_placeholder.pack_forget()

    def show_decompressed_image(self, path):
        img = Image.open(path)
        
        # Set maximum dimensions (you can adjust these)
        max_width = 500
        max_height = 500
        
        # Calculate scaling factor while maintaining aspect ratio
        img_ratio = img.width / img.height
        
        if img.width > max_width or img.height > max_height:
            if img_ratio > 1:
                # Landscape image
                new_width = max_width
                new_height = int(max_width / img_ratio)
            else:
                # Portrait image
                new_height = max_height
                new_width = int(max_height * img_ratio)
            
            # Resize with high-quality filter
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create rounded image
        rounded_img = self.create_rounded_image(img, 25)
        self.decompressed_img = ImageTk.PhotoImage(rounded_img)

        if self.decompressed_panel:
            self.decompressed_panel.config(image=self.decompressed_img)
        else:
            self.decompressed_panel = tk.Label(self.decompressed_frame, image=self.decompressed_img, bg=self.frame_bg)
            self.decompressed_panel.pack(expand=True)
                
        # Remove placeholder if visible
        if self.decompressed_placeholder.winfo_viewable():
            self.decompressed_placeholder.pack_forget()

    def create_rounded_image(self, img, radius):
        """Create an image with rounded corners"""
        mask = Image.new('L', img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle on mask
        width, height = img.size
        mask_draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)
        
        # Apply mask
        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(img, mask=mask)
        return result

    # Compress popup window
    def open_compress_window(self):
        popup = Toplevel(self.root)
        popup.title("Compression Settings")
        popup.geometry("350x280")
        popup.configure(bg=self.bg_color)
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Position in center of parent window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (350 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (280 // 2)
        popup.geometry(f"+{x}+{y}")

        tk.Label(
            popup, 
            text="Compression Parameters", 
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=15)

        # Input fields
        input_frame = tk.Frame(popup, bg=self.bg_color)
        input_frame.pack(pady=15, padx=25, fill="x")
        
        tk.Label(
            input_frame, 
            text="Block Height:", 
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w", pady=8)
        bh_entry = tk.Entry(input_frame, width=15, relief="flat", bg="#f0f0f5")
        bh_entry.grid(row=0, column=1, sticky="e", pady=8)

        tk.Label(
            input_frame, 
            text="Block Width:", 
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky="w", pady=8)
        bw_entry = tk.Entry(input_frame, width=15, relief="flat", bg="#f0f0f5")
        bw_entry.grid(row=1, column=1, sticky="e", pady=8)

        tk.Label(
            input_frame, 
            text="Quantization Level (k):", 
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 10)
        ).grid(row=2, column=0, sticky="w", pady=8)
        k_entry = tk.Entry(input_frame, width=15, relief="flat", bg="#f0f0f5")
        k_entry.grid(row=2, column=1, sticky="e", pady=8)

        def confirm_settings():
            # Placeholder – backend developer will connect here
            messagebox.showinfo("Compression", "Compression settings submitted.")
            popup.destroy()

        button_frame = tk.Frame(popup, bg=self.bg_color)
        button_frame.pack(pady=15)
        
        RoundedButton(
            button_frame, 
            text="Start Compression", 
            command=confirm_settings,
            bg=self.button_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=140,
            height=35
        ).pack(side="left", padx=8)
        
        RoundedButton(
            button_frame, 
            text="Cancel", 
            command=popup.destroy,
            bg="#6c757d",
            fg="white",
            font=("Arial", 10),
            width=100,
            height=35
        ).pack(side="left", padx=8)

    # NEW: Decompress popup window (matching design)
    def open_decompress_window(self):
        if not self.current_image_path:
            self.show_styled_error("Error", "Please select an original image first.")  # FIXED: self.show_styled_error
            return

        popup = Toplevel(self.root)
        popup.title("Decompression Settings")
        popup.geometry("350x280")
        popup.configure(bg=self.bg_color)
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Position in center of parent window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (350 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (280 // 2)  # Fixed height calculation
        popup.geometry(f"+{x}+{y}")

        tk.Label(
            popup, 
            text="Decompression Parameters", 
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=15)

        # Input fields for decompression
        input_frame = tk.Frame(popup, bg=self.bg_color)
        input_frame.pack(pady=15, padx=25, fill="x")
        
        base = os.path.splitext(os.path.basename(self.current_image_path))[0]
        
        # Show which files will be loaded
        tk.Label(
            input_frame, 
            text="Files to load:", 
            bg=self.bg_color,
            fg=self.text_color,
            font=("Arial", 10, "bold")
        ).grid(row=0, column=0, sticky="w", pady=5)

        # File list with rounded backgrounds
        files_frame = tk.Frame(input_frame, bg=self.bg_color)
        files_frame.grid(row=1, column=0, columnspan=2, sticky="we", pady=10)
        
        file_names = [f"{base}_codebook.json", f"{base}_labels.json"]
        for i, file_name in enumerate(file_names):
            file_canvas = tk.Canvas(files_frame, bg=self.bg_color, highlightthickness=0, width=280, height=25)
            file_canvas.pack(pady=3)
            self.draw_rounded_rect(file_canvas, 280, 25, 12, self.placeholder_bg)
            file_canvas.create_text(140, 12, text=file_name, fill=self.text_color, font=("Arial", 9))

        def start_decompression():
            # Placeholder – backend developer will connect here
            messagebox.showinfo("Decompress", "Decompression started successfully!")
            popup.destroy()
            # After decompression, you can show the decompressed image:
            # self.show_decompressed_image("path_to_decompressed_image.png")

        button_frame = tk.Frame(popup, bg=self.bg_color)
        button_frame.pack(pady=15)
        
        RoundedButton(
            button_frame, 
            text="Start Decompression", 
            command=start_decompression,
            bg=self.button_color,
            fg="white",
            font=("Arial", 10, "bold"),
            width=150,
            height=35
        ).pack(side="left", padx=8)
        
        RoundedButton(
            button_frame, 
            text="Cancel", 
            command=popup.destroy,
            bg="#6c757d",
            fg="white",
            font=("Arial", 10),
            width=100,
            height=35
        ).pack(side="left", padx=8)

    # show generated files popup
    def show_files(self):
        if not self.current_image_path:
            self.show_styled_error("Error", "No image selected.")  # FIXED: self.show_styled_error
            return

        base = os.path.splitext(os.path.basename(self.current_image_path))[0]
        popup = Toplevel(self.root)
        popup.title("Generated Files")
        popup.geometry("300x280")
        popup.configure(bg=self.bg_color)
        popup.resizable(False, False)
        
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        
        # Position in center of parent window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (300 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (280 // 2)  # Fixed height calculation
        popup.geometry(f"+{x}+{y}")

        tk.Label(
            popup, 
            text="Generated Files", 
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=15)

        file_frame = tk.Frame(popup, bg=self.bg_color)
        file_frame.pack(pady=10)
        
        # Create rounded file labels
        for file_name in [f"{base}_codebook.txt", f"{base}_labels.bin", f"{base}_labels.json"]:
            file_canvas = tk.Canvas(file_frame, bg=self.bg_color, highlightthickness=0, width=250, height=30)
            file_canvas.pack(pady=5)
            self.draw_rounded_rect(file_canvas, 250, 30, 15, self.placeholder_bg)
            file_canvas.create_text(125, 15, text=file_name, fill=self.text_color, font=("Arial", 9))

        RoundedButton(
            popup, 
            text="Close", 
            command=popup.destroy,
            bg=self.button_color,
            fg="white",
            font=("Arial", 10),
            width=100,
            height=35
        ).pack(pady=10)

    # Reset images
    def reset_images(self):
        if self.original_panel:
            self.original_panel.pack_forget()
            self.original_panel = None
            
        if self.decompressed_panel:
            self.decompressed_panel.pack_forget()
            self.decompressed_panel = None

        # Clear the image path textbox
        self.path_entry.delete(0, tk.END)
    
        # Clear the current image path
        self.current_image_path = None

        self.original_img = None
        self.decompressed_img = None
        
        # Show placeholders again
        self.original_placeholder.pack(expand=True)
        self.decompressed_placeholder.pack(expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = VQ_GUI(root)
    root.mainloop()