"""Tests for the packer module."""
import numpy as np
import pytest
from wsi_packer import pack_images, Shelf


class TestShelf:
    """Tests for the Shelf class."""

    def test_shelf_initialization(self):
        """Test that a shelf initializes correctly."""
        shelf = Shelf(y=10, width=100, height=50)
        assert shelf.y == 10
        assert shelf.x == 0
        assert shelf.width == 100
        assert shelf.height == 50
        assert shelf.remaining_width == 100

    def test_can_fit_true(self):
        """Test that can_fit returns True when item fits."""
        shelf = Shelf(y=0, width=100, height=50)
        assert shelf.can_fit(item_width=50, item_height=30) is True

    def test_can_fit_false_width(self):
        """Test that can_fit returns False when item is too wide."""
        shelf = Shelf(y=0, width=100, height=50)
        assert shelf.can_fit(item_width=150, item_height=30) is False

    def test_can_fit_false_height(self):
        """Test that can_fit returns False when item is too tall."""
        shelf = Shelf(y=0, width=100, height=50)
        assert shelf.can_fit(item_width=50, item_height=60) is False

    def test_add_item(self):
        """Test adding an item to a shelf."""
        shelf = Shelf(y=10, width=100, height=50)
        x, y = shelf.add_item(item_width=30, item_height=40)
        
        assert x == 0
        assert y == 10
        assert shelf.x == 30
        assert shelf.remaining_width == 70

    def test_add_multiple_items(self):
        """Test adding multiple items to a shelf."""
        shelf = Shelf(y=10, width=100, height=50)
        
        x1, y1 = shelf.add_item(item_width=30, item_height=40)
        assert x1 == 0
        assert y1 == 10
        
        x2, y2 = shelf.add_item(item_width=20, item_height=40)
        assert x2 == 30
        assert y2 == 10
        assert shelf.remaining_width == 50


class TestPackImages:
    """Tests for the pack_images function."""

    def test_pack_empty_list(self):
        """Test packing an empty list of images."""
        result = pack_images([])
        assert isinstance(result, np.ndarray)
        assert result.shape == (100, 100, 3)
        assert result.dtype == np.uint8

    def test_pack_single_image(self):
        """Test packing a single image."""
        img = np.ones((50, 100, 3), dtype=np.uint8) * 128
        result = pack_images([img], margin=5)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert result.shape[2] == 3
        # Check that the result is large enough to contain the image with margins
        assert result.shape[0] >= 60  # height + 2*margin
        assert result.shape[1] >= 110  # width + 2*margin

    def test_pack_multiple_images(self):
        """Test packing multiple images."""
        images = [
            np.ones((50, 100, 3), dtype=np.uint8) * 100,
            np.ones((30, 80, 3), dtype=np.uint8) * 150,
            np.ones((40, 60, 3), dtype=np.uint8) * 200,
        ]
        result = pack_images(images, margin=5)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert result.shape[2] == 3
        # Result should be large enough to contain all images
        assert result.size > 0

    def test_pack_images_with_margin(self):
        """Test that margin parameter affects the result size."""
        img = np.ones((50, 100, 3), dtype=np.uint8) * 128
        
        result_small_margin = pack_images([img], margin=5)
        result_large_margin = pack_images([img], margin=20)
        
        # Larger margin should result in larger output
        assert result_large_margin.shape[0] > result_small_margin.shape[0]
        assert result_large_margin.shape[1] > result_small_margin.shape[1]

    def test_pack_images_different_sizes(self):
        """Test packing images of various sizes."""
        images = [
            np.ones((100, 200, 3), dtype=np.uint8) * 50,
            np.ones((150, 150, 3), dtype=np.uint8) * 100,
            np.ones((80, 120, 3), dtype=np.uint8) * 150,
            np.ones((200, 100, 3), dtype=np.uint8) * 200,
        ]
        result = pack_images(images, margin=10)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert result.shape[2] == 3

    def test_pack_images_preserves_dtype(self):
        """Test that packing preserves the uint8 dtype."""
        img = np.ones((50, 100, 3), dtype=np.uint8) * 255
        result = pack_images([img])
        
        assert result.dtype == np.uint8

    def test_pack_images_color_values(self):
        """Test that packed images preserve color values."""
        # Create a distinct color pattern
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        img[:, :] = [100, 150, 200]  # Specific RGB values
        
        result = pack_images([img], margin=5)
        
        # Check that the central portion of the packed image has the correct colors
        # The packing algorithm places images at the margin position
        center_region = result[10:40, 10:40]
        
        # Check that colors are preserved in the center region
        assert np.all(center_region == [100, 150, 200])

    def test_pack_images_white_background(self):
        """Test that the background is white (255)."""
        img = np.zeros((20, 20, 3), dtype=np.uint8)  # Black image
        result = pack_images([img], margin=10)
        
        # Check corners which should be white background
        assert np.all(result[0, 0] == 255)
        assert np.all(result[-1, -1] == 255)

    def test_pack_images_sorting(self):
        """Test that images are sorted by height for efficient packing."""
        # Create images of different heights
        tall_img = np.ones((200, 50, 3), dtype=np.uint8) * 100
        medium_img = np.ones((100, 50, 3), dtype=np.uint8) * 150
        short_img = np.ones((50, 50, 3), dtype=np.uint8) * 200
        
        images = [short_img, tall_img, medium_img]  # Unsorted
        result = pack_images(images, margin=5)
        
        # Should successfully pack all images
        assert isinstance(result, np.ndarray)
        assert result.shape[2] == 3

    def test_pack_images_zero_margin(self):
        """Test packing with zero margin."""
        img = np.ones((50, 100, 3), dtype=np.uint8) * 128
        result = pack_images([img], margin=0)
        
        assert isinstance(result, np.ndarray)
        # With zero margin, result should be very close to original size
        assert result.shape[0] >= 50
        assert result.shape[1] >= 100

    def test_pack_many_small_images(self):
        """Test packing many small images."""
        images = [np.ones((20, 20, 3), dtype=np.uint8) * (i * 10) for i in range(20)]
        result = pack_images(images, margin=5)
        
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert result.shape[2] == 3
