# Puzzle Slider Captcha Solver

A robust, OpenCV-based library for solving "slider" style captchas (like GeeTest, Shopee, etc.) where a puzzle piece needs to be matched to a hole in the background.

Unlike AI-based solvers, this library uses advanced Template Matching and Image Processing techniques to find pixel-perfect matches, making it extremely fast and lightweight.

## Features

- **High Precision**: Uses `cv2.TM_CCOEFF_NORMED` with sub-pixel refinement for accurate coordinate detection.
- **Robust Transforms**: Includes built-in image transformations (Edge Detection, Normalization) to handle various captcha styles.
- **Lightweight**: Only depends on `opencv-python` and `numpy`.
- **Easy Visualization**: Built-in methods to debug and visualize the matching result.

## Installation

```bash
pip install puzzle-slider-captcha
```

## Usage

```python
from puzzle_slider_captcha import PuzzleCaptchaSolver

# Initialize solver
solver = PuzzleCaptchaSolver()

# Solve from files
result = solver.handle_file("background.png", "puzzle_piece.png")

# Or solve from bytes
# result = solver.handle_bytes(bg_bytes, puzzle_bytes)

print(f"Target X: {result.x}, Target Y: {result.y}")

# Visualize debug result
result.visualize_and_save("debug_result.png")
```

## Requirements

- Python 3.8+
- OpenCV
- Numpy
