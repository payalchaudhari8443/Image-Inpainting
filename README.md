# Image Inpainting

## Overview

**Image Inpainting** is a GUI-based application that allows users to repair or reconstruct damaged or missing parts of an image by drawing a mask over the area they want to restore. The program offers two methods of inpainting: **Telea** and **Navier-Stokes**. It also provides the ability to save the inpainted image and store mask details in a database.

## Features

- **Image Loading**: Select and load images in `.jpg`, `.jpeg`, or `.png` format.
- **Drawing Mask**: Draw a mask over areas in the image that need to be restored using the mouse.
- **Inpainting Methods**: Choose between two inpainting algorithms—`Telea` and `Navier-Stokes`.
- **Save Inpainted Image**: Save the output image after inpainting is complete.
- **Database Integration**: Save mask details to a local SQLite database for future reference.
- **File Handling**: Automatically save mask images and details in JSON and text format for better tracking.

## Requirements

- Python 3.x
- Required Python libraries: 
  - `opencv-python`
  - `numpy`
  - `Pillow`
  - `tkinter`
  - `sqlite3`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Image-Inpainting.git
