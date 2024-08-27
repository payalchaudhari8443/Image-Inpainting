import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import sqlite3
import os

class ImageInpaintingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Inpainting with Realistic Details")
        self.root.configure(bg='darkblue')

        self.welcome_label = tk.Label(root, text="Welcome to Image Inpainting!", font=("Helvetica", 16), bg='darkblue', fg='white')
        self.welcome_label.pack(pady=10)

        try:
            self.gallery_icon = ImageTk.PhotoImage(Image.open("C:/Users/shubh/OneDrive/Desktop/ImageInpaintingProject/gallery_icon.jpeg").resize((40, 40), Image.LANCZOS))
        except FileNotFoundError:
            messagebox.showerror("Error", "Gallery icon image not found. Please check the file path.")
            self.root.destroy()
            return

        self.load_button = tk.Button(root, image=self.gallery_icon, command=self.load_image, bd=0, bg='darkblue')
        self.load_button.pack(pady=10)

        self.method_frame = tk.Frame(root, bg='darkblue')
        self.inpaint_button = tk.Button(root, text="Inpaint Image", command=self.inpaint_image, state=tk.DISABLED, bg='lightgrey')
        self.save_button = tk.Button(root, text="Save Inpainted Image", command=self.save_inpainted_image, state=tk.DISABLED, bg='lightgrey')

        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.image = None
        self.mask = None
        self.drawing = False
        self.inpaint_method = None

        self.canvas.config(cursor="hand2")
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_mask)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        self.scale_x = 1
        self.scale_y = 1

        self.setup_database()

    def setup_database(self):
        self.conn = sqlite3.connect('mask_details.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS masks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mask_data TEXT
            )
        ''')
        self.conn.commit()

    def load_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png"), ("All Files", "*.*")))
        if file_path:
            self.image = cv2.imread(file_path)
            self.mask = np.zeros(self.image.shape[:2], np.uint8)
            self.display_image(self.image)

            self.method_frame.pack(pady=10)

            self.method_button1 = tk.Button(self.method_frame, text="Inpaint with Telea", command=lambda: self.set_method(cv2.INPAINT_TELEA), state=tk.NORMAL, bg='lightgrey')
            self.method_button1.pack(side=tk.LEFT, padx=5)

            self.method_button2 = tk.Button(self.method_frame, text="Inpaint with NS", command=lambda: self.set_method(cv2.INPAINT_NS), state=tk.NORMAL, bg='lightgrey')
            self.method_button2.pack(side=tk.LEFT, padx=5)

            self.inpaint_button.pack(side=tk.LEFT, padx=5)
            self.save_button.pack(side=tk.LEFT, padx=5)

            self.inpaint_button.config(state=tk.NORMAL)

    def display_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(image_rgb)
        img = img.resize((600, 400), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)

        self.scale_x = image.shape[1] / 600
        self.scale_y = image.shape[0] / 400

        self.canvas.config(width=600, height=400)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def start_drawing(self, event):
        self.drawing = True
        self.prev_x, self.prev_y = int(event.x * self.scale_x), int(event.y * self.scale_y)

    def draw_mask(self, event):
        if self.drawing:
            current_x, current_y = int(event.x * self.scale_x), int(event.y * self.scale_y)
            cv2.line(self.mask, (self.prev_x, self.prev_y), (current_x, current_y), 255, 5)
            self.prev_x, self.prev_y = current_x, current_y
            mask_display = cv2.addWeighted(self.image, 0.7, cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR), 0.3, 0)
            self.display_image(mask_display)

    def stop_drawing(self, event):
        self.drawing = False

    def set_method(self, method):
        self.inpaint_method = method
        messagebox.showinfo("Method Selected", f"Inpainting method set to {'Telea' if method == cv2.INPAINT_TELEA else 'Navier-Stokes'}")

    def inpaint_image(self):
        if self.inpaint_method is None:
            messagebox.showwarning("Method Not Selected", "Please select an inpainting method first.")
            return

        inpainted_image = cv2.inpaint(self.image, self.mask, inpaintRadius=3, flags=self.inpaint_method)
        self.display_image(inpainted_image)

        self.inpainted_image = inpainted_image
        self.save_button.config(state=tk.NORMAL)
        self.save_mask_details(inpainted_image)

    def save_inpainted_image(self):
        mask_dir = "mask_images"
        os.makedirs(mask_dir, exist_ok=True)
        inpainted_image_path = os.path.join(mask_dir, "inpainted_image.png")
        cv2.imwrite(inpainted_image_path, self.inpainted_image)
        messagebox.showinfo("Save Image", f"Inpainted image saved successfully at: {inpainted_image_path}")

    def save_mask_details(self, inpainted_image):
        mask_dir = "mask_images"
        os.makedirs(mask_dir, exist_ok=True)
        mask_image_path = os.path.join(mask_dir, "mask_image.png")
        cv2.imwrite(mask_image_path, self.mask)

        mask_details = {
            "mask": self.mask.tolist()
        }
        self.cursor.execute('INSERT INTO masks (mask_data) VALUES (?)', (json.dumps(mask_details),))
        self.conn.commit()

        mask_details_text_path = os.path.join(mask_dir, "mask_details.txt")
        with open(mask_details_text_path, 'w') as f:
            f.write(json.dumps(mask_details, indent=4))

        messagebox.showinfo("Save Mask", f"Mask image saved successfully at: {mask_image_path}\nMask details saved to text file at: {mask_details_text_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageInpaintingApp(root)
    root.mainloop()
