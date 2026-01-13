import argparse
from pathlib import Path
import wholeslidedata as wsd
import cv2
import json
import numpy as np
import sys
import os

from packer import pack_images

def main():
    parser = argparse.ArgumentParser(description='Create thumbnail from whole slide image, requires the wholeslidedata package')
    parser.add_argument('input_path', type=str, help='Path to the whole slide image')
    parser.add_argument('output_folder', type=str, help='Output folder for the thumbnail')
    parser.add_argument('--spacing', type=float, default=8.0, help='Spacing for thumbnail (default: 8.0)')
    parser.add_argument('--tissue_mask', type=str, default=None, help='Path to tissue mask GeoJSON file (optional)')
    parser.add_argument('--mask_spacing', type=float, default=0.5, help='Spacing of the tissue mask (default: 0.5 um/px)')
    parser.add_argument('--target_size', type=int, default=3000, help='Target size for longest dimension in pixels (default: 3000)')
    parser.add_argument('--pack', action='store_true', help='Pack tissue regions efficiently to maximize information density')
    
    args = parser.parse_args()
    
    # Create output folder if it doesn't exist
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Open the whole slide image
    wsi = wsd.WholeSlideImage(args.input_path)
    
    # Load tissue mask if provided
    tissue_bounds = None
    tissue_polygons = None
    if args.tissue_mask:
        tissue_bounds, tissue_polygons = get_tissue_bounds_from_geojson(args.tissue_mask, args.mask_spacing)
    
    # Create the thumbnail
    create_thumbnail(wsi, output_folder, spacing=args.spacing, tissue_bounds=tissue_bounds, 
                    tissue_polygons=tissue_polygons, mask_spacing=args.mask_spacing,
                    target_size=args.target_size, pack_regions=args.pack)
    
    print(f"Thumbnail created successfully in {output_folder}")

def get_tissue_bounds_from_geojson(geojson_path, mask_spacing):
    """
    Extract bounding box and polygons from GeoJSON tissue mask.
    Returns tuple: (bounds, polygons) where bounds is (x_min, y_min, x_max, y_max) 
    and polygons is a list of polygon coordinate arrays.
    """
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    all_coords = []
    polygons = []
    
    for feature in geojson_data['features']:
        geometry = feature['geometry']
        if geometry['type'] == 'Polygon':
            # Store each polygon separately
            for ring in geometry['coordinates']:
                coords = np.array(ring)
                polygons.append(coords)
                all_coords.extend(ring)
        elif geometry['type'] == 'MultiPolygon':
            for polygon in geometry['coordinates']:
                for ring in polygon:
                    coords = np.array(ring)
                    polygons.append(coords)
                    all_coords.extend(ring)
    
    if not all_coords:
        return None, None
    
    coords_array = np.array(all_coords)
    x_min, y_min = coords_array.min(axis=0)
    x_max, y_max = coords_array.max(axis=0)
    
    print(f"Tissue bounds at {mask_spacing} um/px: x=[{x_min:.1f}, {x_max:.1f}], y=[{y_min:.1f}, {y_max:.1f}]")
    print(f"Tissue region size: {x_max - x_min:.1f} x {y_max - y_min:.1f}")
    print(f"Number of tissue polygons: {len(polygons)}")
    
    return (x_min, y_min, x_max, y_max), polygons

def create_thumbnail(wsi, output_folder, spacing=8.0, tissue_bounds=None, tissue_polygons=None, mask_spacing=0.5, target_size=3000, pack_regions=False):
    """
    Create thumbnail, optionally cropping to tissue bounds and masking non-tissue regions.
    
    Args:
        wsi: WholeSlideImage object
        output_folder: Path to output folder
        spacing: Spacing for the thumbnail (um/px)
        tissue_bounds: Optional tuple (x_min, y_min, x_max, y_max) at mask spacing
        tissue_polygons: Optional list of polygon coordinate arrays
        mask_spacing: Spacing of the tissue mask (um/px)
        target_size: Target size for longest dimension in pixels
        pack_regions: Whether to pack tissue regions efficiently
    """
    # Get the full slide at the desired spacing
    slide = wsi.get_slide(spacing)
    
    if tissue_bounds is not None and pack_regions:
        # Extract and pack individual tissue regions
        slide_to_save = extract_and_pack_tissue(slide, tissue_bounds, tissue_polygons, spacing, mask_spacing, target_size)
    elif tissue_bounds is not None:
        # Standard cropping and masking
        x_min, y_min, x_max, y_max = tissue_bounds
        
        # Calculate scaling factor from mask spacing to thumbnail spacing
        scale = spacing / mask_spacing
        
        # Convert bounds to thumbnail coordinates
        x_min_thumb = int(x_min / scale)
        y_min_thumb = int(y_min / scale)
        x_max_thumb = int(np.ceil(x_max / scale))
        y_max_thumb = int(np.ceil(y_max / scale))
        
        # Ensure bounds are within image dimensions
        h, w = slide.shape[:2]
        x_min_thumb = max(0, x_min_thumb)
        y_min_thumb = max(0, y_min_thumb)
        x_max_thumb = min(w, x_max_thumb)
        y_max_thumb = min(h, y_max_thumb)
        
        # Crop the slide
        cropped_slide = slide[y_min_thumb:y_max_thumb, x_min_thumb:x_max_thumb]
        
        print(f"Cropped thumbnail from {slide.shape} to {cropped_slide.shape}")
        print(f"Crop coordinates: x=[{x_min_thumb}, {x_max_thumb}], y=[{y_min_thumb}, {y_max_thumb}]")
        
        # Apply tissue mask if polygons are provided
        if tissue_polygons is not None:
            # Create a binary mask for the cropped region
            mask = np.zeros(cropped_slide.shape[:2], dtype=np.uint8)
            
            # Convert each polygon to thumbnail coordinates and fill
            for polygon in tissue_polygons:
                # Scale and translate polygon coordinates
                scaled_polygon = polygon / scale
                translated_polygon = scaled_polygon - np.array([x_min_thumb, y_min_thumb])
                
                # Convert to integer coordinates
                polygon_int = translated_polygon.astype(np.int32)
                
                # Fill the polygon in the mask
                cv2.fillPoly(mask, [polygon_int], 1)
            
            # Apply mask - set non-tissue regions to white (255) or black (0)
            masked_slide = cropped_slide.copy()
            masked_slide[mask == 0] = 255  # White background for non-tissue regions
            
            print(f"Applied tissue mask: {np.sum(mask > 0) / mask.size * 100:.2f}% tissue coverage")
            slide_to_save = masked_slide
        else:
            slide_to_save = cropped_slide
        
        # Resize to target size
        slide_to_save = resize_to_target(slide_to_save, target_size)
    else:
        slide_to_save = slide
        slide_to_save = resize_to_target(slide_to_save, target_size)
    
    output_path = output_folder / (Path(wsi.path).stem + ".jpg")
    # Match original code: convert BGR to RGB before cv2.imwrite
    slide_to_save = cv2.cvtColor(slide_to_save, cv2.COLOR_BGR2RGB)
    cv2.imwrite(str(output_path), slide_to_save, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"Thumbnail saved at {output_path}")

def resize_to_target(image, target_size):
    """Resize image so the longest dimension is target_size pixels."""
    h, w = image.shape[:2]
    if max(h, w) <= target_size:
        print(f"Image size {image.shape[:2]} is already within target, no resizing needed")
        return image
    
    if h > w:
        new_h = target_size
        new_w = int(w * target_size / h)
    else:
        new_w = target_size
        new_h = int(h * target_size / w)
    
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    print(f"Resized from {image.shape[:2]} to {resized.shape[:2]}")
    return resized

def extract_and_pack_tissue(slide, tissue_bounds, tissue_polygons, spacing, mask_spacing, target_size):
    """
    Extract individual tissue regions and pack them efficiently.
    
    Args:
        slide: Full slide image
        tissue_bounds: Tuple (x_min, y_min, x_max, y_max) at mask spacing
        tissue_polygons: List of polygon coordinate arrays
        spacing: Thumbnail spacing (um/px)
        mask_spacing: Mask spacing (um/px)
        target_size: Target size for longest dimension
    
    Returns:
        Packed image with tissue regions
    """
    scale = spacing / mask_spacing
    
    # Extract bounding box for each polygon and extract the tissue region
    tissue_regions = []
    
    for polygon in tissue_polygons:
        # Get bounding box for this polygon
        poly_min = polygon.min(axis=0)
        poly_max = polygon.max(axis=0)
        
        # Convert to thumbnail coordinates
        x_min = int(poly_min[0] / scale)
        y_min = int(poly_min[1] / scale)
        x_max = int(np.ceil(poly_max[0] / scale))
        y_max = int(np.ceil(poly_max[1] / scale))
        
        # Ensure within slide bounds
        h, w = slide.shape[:2]
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(w, x_max)
        y_max = min(h, y_max)
        
        if x_max <= x_min or y_max <= y_min:
            continue
        
        # Extract region
        region = slide[y_min:y_max, x_min:x_max].copy()
        
        # Create mask for this region
        region_mask = np.zeros(region.shape[:2], dtype=np.uint8)
        scaled_polygon = polygon / scale
        translated_polygon = scaled_polygon - np.array([x_min, y_min])
        polygon_int = translated_polygon.astype(np.int32)
        cv2.fillPoly(region_mask, [polygon_int], 1)
        
        # Apply mask (set background to white)
        region[region_mask == 0] = 255
        
        tissue_regions.append(region)
    
    print(f"Extracted {len(tissue_regions)} tissue regions")
    
    if not tissue_regions:
        # Fallback to simple crop if no regions extracted
        x_min, y_min, x_max, y_max = tissue_bounds
        x_min = int(x_min / scale)
        y_min = int(y_min / scale)
        x_max = int(np.ceil(x_max / scale))
        y_max = int(np.ceil(y_max / scale))
        h, w = slide.shape[:2]
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(w, x_max)
        y_max = min(h, y_max)
        return resize_to_target(slide[y_min:y_max, x_min:x_max], target_size)
    
    # Use simple packing with our custom packer
    print("Packing tissue regions with shelf packing algorithm...")
    packed_img = pack_images(tissue_regions, margin=5)
    print(f"Packed image size: {packed_img.shape[:2]}")
    
    # Resize to target size
    packed_img = resize_to_target(packed_img, target_size)
    
    return packed_img

if __name__ == "__main__":
    main()


