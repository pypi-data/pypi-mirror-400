"""
Simple rectangle packer for images that preserves color accuracy.
Uses a shelf-packing algorithm (First Fit Decreasing Height).
"""
import numpy as np
from typing import List, Tuple


class Shelf:
    """Represents a horizontal shelf in the bin packing."""
    def __init__(self, y: int, width: int, height: int):
        self.y = y  # Y position of shelf
        self.x = 0  # Current X position (where next item goes)
        self.width = width  # Maximum width available
        self.height = height  # Height of this shelf
        self.remaining_width = width
    
    def can_fit(self, item_width: int, item_height: int) -> bool:
        """Check if an item can fit on this shelf."""
        return item_width <= self.remaining_width and item_height <= self.height
    
    def add_item(self, item_width: int, item_height: int) -> Tuple[int, int]:
        """Add item to shelf and return its (x, y) position."""
        x = self.x
        y = self.y
        self.x += item_width
        self.remaining_width -= item_width
        return x, y


def pack_images(images: List[np.ndarray], margin: int = 5) -> np.ndarray:
    """
    Pack multiple images into a single image using shelf packing algorithm.
    
    Args:
        images: List of numpy arrays (images) to pack
        margin: Margin in pixels between images
    
    Returns:
        Single numpy array containing all packed images
    """
    if not images:
        return np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    # Get dimensions for each image with index
    items = [(i, img.shape[1], img.shape[0], img) for i, img in enumerate(images)]  # (index, width, height, image)
    
    # Sort by height (descending) for better packing
    items.sort(key=lambda x: x[2], reverse=True)
    
    # Estimate container width based on total area
    total_area = sum(w * h for _, w, h, _ in items)
    # Add margin area
    margin_area = sum((w + 2*margin) * (h + 2*margin) - w*h for _, w, h, _ in items)
    total_with_margin = total_area + margin_area
    
    # Start with a square-ish container
    container_width = int(np.sqrt(total_with_margin * 1.2))
    
    # Pack items and track positions
    shelves = []
    current_y = margin
    max_width_used = 0
    positions = {}  # Maps index to (x, y) position
    
    for idx, item_width, item_height, img in items:
        # Add margins to dimensions
        item_w_margin = item_width + margin
        item_h_margin = item_height + margin
        
        # Try to find a shelf that can fit this item
        placed = False
        for shelf in shelves:
            if shelf.can_fit(item_w_margin, item_h_margin):
                x, y = shelf.add_item(item_w_margin, item_h_margin)
                positions[idx] = (x, y)
                placed = True
                max_width_used = max(max_width_used, x + item_w_margin)
                break
        
        # If no shelf can fit it, create a new shelf
        if not placed:
            shelf = Shelf(current_y, container_width, item_h_margin)
            x, y = shelf.add_item(item_w_margin, item_h_margin)
            positions[idx] = (x, y)
            shelves.append(shelf)
            current_y += item_h_margin
            max_width_used = max(max_width_used, item_w_margin)
    
    # Calculate final container size
    final_width = max_width_used + margin
    final_height = current_y + margin
    
    # Create canvas
    canvas = np.ones((final_height, final_width, 3), dtype=np.uint8) * 255
    
    # Place images on canvas
    for idx, item_width, item_height, img in items:
        x, y = positions[idx]
        canvas[y:y+item_height, x:x+item_width] = img
    
    return canvas
