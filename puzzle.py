from math import sqrt
from pathlib import Path
from tkinter import Tk, Canvas, messagebox
from PIL import Image, ImageTk
import random


# Load and process the image
def load_image(path, pieces_per_row, screen_width):
    image = Image.open(path)
    print(f"Loaded image size: {image.size}")

    # Scale the image to fit half the screen width
    scaled_image = scale_image(image, max_width=screen_width // 2)
    scaled_width, scaled_height = scaled_image.size
    print(f"Scaled image size: {scaled_image.size}")

    piece_width = scaled_width // pieces_per_row
    piece_height = scaled_height // pieces_per_row

    pieces_and_target_positions = dict()

    total_pieces = 0
    for x in range(0, scaled_width, piece_width):
        for y in range(0, scaled_height, piece_height):
            box = (x, y, x + piece_width, y + piece_height)
            piece = scaled_image.crop(box)
            total_pieces += 1
            pieces_and_target_positions[(x, y)] = (total_pieces, piece)
            print(f"Created piece: {box}")  # Debugging line

    print(f"Pieces and target positions: {pieces_and_target_positions}")

    return pieces_and_target_positions, scaled_image, piece_width, piece_height


def scale_image(image, max_width=None, max_height=None):
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height

    if max_width is not None:
        new_width = min(max_width, original_width)
        new_height = int(new_width / aspect_ratio)
    elif max_height is not None:
        new_height = min(max_height, original_height)
        new_width = int(new_height * aspect_ratio)

    return image.resize((new_width, new_height))


def start_game_window(image, org_pos_pieces, screen_width, screen_height, piece_width, piece_height, show_bg_pic=True):
    window = Tk()
    window.title("Puzzle Game")

    canvas_width = image.width
    canvas_height = image.height
    pieces_per_row = canvas_width // piece_width

    # Set window size and position
    window_width = canvas_width * 2
    window_height = canvas_height

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Left side for puzzle pieces
    left_frame = Canvas(window, width=canvas_width, height=canvas_height, bg='white')
    left_frame.pack(side="left")

    # Right side for the background image
    right_frame = Canvas(window, width=canvas_width, height=canvas_height, bg='white')
    right_frame.pack(side="right")

    overlay_canvas = Canvas(window, width=window_width, height=window_height, bg='white', highlightthickness=0)
    overlay_canvas.place(x=0, y=0)  # This canvas covers the entire window

    photo_images = []  # Keep references to PhotoImage objects to avoid garbage collection

    # Display the background image (80% transparent)
    if show_bg_pic:
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        transparent_image = image.copy()
        transparent_image.putalpha(20)  # Apply transparency
        background_image = ImageTk.PhotoImage(transparent_image)
        overlay_canvas.create_image(canvas_width, 0, image=background_image, anchor='nw')
        photo_images.append(background_image)  # Store the reference

    pieces_on_canvas = {}  # Dictionary to store references to the pieces on the canvas, i.e. state, position, etc.

    pieces = list(org_pos_pieces.values())  # Convert dictionary values to a list
    random.shuffle(pieces)  # Shuffle the pieces
    # Display the scaled puzzle pieces
    for i, (pid, piece) in enumerate(pieces):
        piece_image = ImageTk.PhotoImage(piece)
        photo_images.append(piece_image)  # Store the reference

        # Get target pos key from pieces for this piece (=value)
        tar_x, tar_y = list(org_pos_pieces.keys())[[v[0] for v in list(org_pos_pieces.values())].index(pid)]

        x = (i % pieces_per_row) * piece_width
        y = (i // pieces_per_row) * piece_height

        if y < canvas_height:  # Make sure the piece is within the canvas height
            piece_id = overlay_canvas.create_image(x, y, image=piece_image, anchor='nw')
            pieces_on_canvas[piece_id] = {"img": piece, "original_position": (x,y), "target_pos": (tar_x +canvas_width, tar_y), "solved": False}
            overlay_canvas.bind("<ButtonPress-1>", lambda event, oc=overlay_canvas, pc=pieces_on_canvas: on_drag_start(event, oc, pc))
            overlay_canvas.bind("<B1-Motion>", lambda event, oc=overlay_canvas: on_drag_motion(event, oc))
            overlay_canvas.bind("<ButtonRelease-1>", lambda event, oc=overlay_canvas, w=window: on_drop(event, oc, w))

            print(f"Displaying piece at: {x}, {y}")  # Debugging line
        else:
            print(f"Skipping piece at: {x}, {y} - Outside canvas bounds")

    window.mainloop()


def on_drag_start(event, overlay_canvas, pieces_on_canvas):
    # Get the item ID of the canvas item under the cursor
    x, y = event.x, event.y
    item_id = overlay_canvas.find_closest(x, y)[0]
    # Store initial positions and item ID for dragging
    overlay_canvas.drag_data = {"x": x, "y": y, "item_id": item_id, "original_position": pieces_on_canvas[item_id]["original_position"],
                                "target_pos": pieces_on_canvas[item_id]["target_pos"], "piece_size": pieces_on_canvas[item_id]["img"].size,
                                "pieces_on_canvas": pieces_on_canvas}


def on_drag_motion(event, overlay_canvas):
    deltaX = event.x - overlay_canvas.drag_data["x"]
    deltaY = event.y - overlay_canvas.drag_data["y"]
    overlay_canvas.move(overlay_canvas.drag_data["item_id"], deltaX, deltaY)
    # Update position for next motion event
    overlay_canvas.drag_data["x"] = event.x
    overlay_canvas.drag_data["y"] = event.y


def calculate_overlap(x, y, correct_x, correct_y, width, height):
    # Calculate the area of overlap
    overlap_x = max(0, min(x + width, correct_x + width) - max(x, correct_x))
    overlap_y = max(0, min(y + height, correct_y + height) - max(y, correct_y))
    overlap_area = overlap_x * overlap_y

    # Calculate the total area of a puzzle piece
    total_area = width * height

    # Calculate the proportion of the area that is overlapping
    if total_area == 0:
        return 0
    else:
        return overlap_area / total_area


def on_drop(event, overlay_canvas, window):
    item_id = overlay_canvas.drag_data["item_id"]
    x, y = overlay_canvas.coords(item_id)  # Current position of the piece

    # Assuming you have a function to get the correct position for this piece
    correct_x, correct_y = overlay_canvas.drag_data["target_pos"]
    piece_width, piece_height = overlay_canvas.drag_data["piece_size"]

    # Calculate overlap (example calculation, adjust as needed)
    overlap = calculate_overlap(x, y, correct_x, correct_y, piece_width, piece_height)

    if overlap < 0.6:  # Less than 80% overlap
        # Move back to original position
        original_x, original_y = overlay_canvas.drag_data["original_position"]
        overlay_canvas.coords(item_id, original_x, original_y)
    else:
        # Snap to correct position
        overlay_canvas.drag_data["pieces_on_canvas"][item_id]["solved"] = True
        overlay_canvas.coords(item_id, correct_x, correct_y)

    # Check for completion after a delay to allow UI to update
    overlay_canvas.after(50, check_and_celebrate, overlay_canvas, window)


def check_and_celebrate(overlay_canvas, window):
    if check_puzzle_complete(pieces_on_canvas=overlay_canvas.drag_data["pieces_on_canvas"]):
        print("Puzzle complete!")
        # Schedule the confetti animation to start after a short delay
        overlay_canvas.after(50, lambda: show_confetti_animation(overlay_canvas, window))
        # Schedule the dialog to appear after the animation has had time to start
        animation_time_in_ms = 5000
        overlay_canvas.after(animation_time_in_ms, lambda: ask_to_play_again(window))


def check_puzzle_complete(pieces_on_canvas):
    completed = all([piece["solved"] for piece in pieces_on_canvas.values()])
    return completed


def update_frame(idx, overlay_canvas, window, confetti_item, frames):
    frame = frames[idx]
    idx += 1  # Next frame index
    if idx == len(frames):
        idx = 0  # Reset to first frame
    overlay_canvas.itemconfig(confetti_item, image=frame)
    window.after(50, update_frame, idx, overlay_canvas, window, confetti_item, frames)


def load_frames(image_path):
    img = Image.open(image_path)
    frames = []
    try:
        while True:
            img.seek(len(frames))  # Move to next frame
            frames.append(ImageTk.PhotoImage(img.copy()))
    except EOFError:
        pass  # We have reached the end of the animation
    return frames


def show_confetti_animation(overlay_canvas, window):
    gif_path = "img/confetti.gif"
    frames = load_frames(gif_path)

    confetti_item = overlay_canvas.create_image(overlay_canvas.winfo_width() // 2,
                                                overlay_canvas.winfo_height() // 2,
                                                image=frames[0])  # Position it in the center
    update_frame(0, overlay_canvas, window, confetti_item, frames)


def ask_to_play_again(window):
    # MacOS not shows any title
    response = messagebox.askyesno("Congrats!", "Congrats! Do you want to play again?", icon=messagebox.QUESTION)
    if response:
        window.destroy()  # Close the old window
        main()  # Restart the game
    else:
        window.destroy()  # Close the old window
        exit()


def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    difficulty_levels = ["easy", "medium", "hard", "expert"]
    total_pieces = [4, 16, 49, 49]
    diff_to_pieces = dict(zip(difficulty_levels, total_pieces))
    mut_exclusive_group = parser.add_mutually_exclusive_group()
    mut_exclusive_group.add_argument("--difficulty", "--lvl", type=str, help="Difficulty level",
                                     choices=difficulty_levels, required=False)
    mut_exclusive_group.add_argument("--pieces", "-p", type=int, help="Number of total pieces",
                                     choices=total_pieces, required=False)
    mut_exclusive_group.add_argument("--random", "-r", action="store_true", help="Random number of pieces",
                                     default=True,
                                     required=False)
    args = parser.parse_args()
    show_bg_pic = True
    if args.difficulty:
        n_pieces = diff_to_pieces[args.difficulty]
        if args.difficulty == "expert":
            show_bg_pic = False
    elif args.pieces:
        n_pieces = args.pieces
    elif args.random:
        n_pieces = random.choice(total_pieces)
    return n_pieces, show_bg_pic


def main():
    images = ["dogs.png", "confetti.png", "car-xmas.png", "santa.png", "monster-puzzle.png"]
    image_path = Path("img", random.choice(images))
    total_pieces, show_bg_pic = get_args()
    pieces_per_row = int(sqrt(total_pieces))
    print(f"Image path: {image_path}")
    print(f"Total pieces: {total_pieces}")
    print(f"Pieces per row: {pieces_per_row}")

    root = Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    pieces, scaled_image, piece_width, piece_height = load_image(image_path, pieces_per_row, screen_width)

    start_game_window(scaled_image, pieces, screen_width, screen_height, piece_width, piece_height, show_bg_pic)


if __name__ == "__main__":
    main()
