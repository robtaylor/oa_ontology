#!/usr/bin/env python3
"""
UML Diagram Parser for OpenAccess Ontology

This script attempts to parse UML diagrams from image files and convert them
to a structured YAML representation that can be integrated with the ontology.

Note: This requires external OCR packages to be installed:
- Tesseract OCR for text recognition
- opencv-python for image processing
- pytesseract as a Python wrapper for Tesseract

Install with:
  pip install pytesseract opencv-python pyyaml
  
You'll also need Tesseract OCR installed on your system:
  On MacOS: brew install tesseract
  On Ubuntu: apt-get install tesseract-ocr
  On Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
"""

import os
import sys
import yaml
import argparse
import re
from pathlib import Path

# These imports will fail if the required packages are not installed
try:
    import cv2
    import pytesseract
    import numpy as np
except ImportError:
    print("Error: Required packages not installed. Please install:")
    print("  pip install pytesseract opencv-python numpy")
    print("And make sure Tesseract OCR is installed on your system")
    sys.exit(1)

class UMLParser:
    """Parser for UML diagrams from image files."""
    
    def __init__(self, image_path):
        """Initialize the parser with an image file."""
        self.image_path = image_path
        
        # Check if the image file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load the image
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Failed to load image: {image_path}")
    
    def preprocess_image(self):
        """Preprocess the image to improve OCR results."""
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding for better results with varying lighting
        binary = cv2.adaptiveThreshold(
            gray, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 
            11, 
            2
        )
        
        # Perform morphological operations to remove noise
        kernel = np.ones((1, 1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Save the preprocessed image for debugging
        debug_dir = os.path.join(os.path.dirname(self.image_path), "debug")
        os.makedirs(debug_dir, exist_ok=True)
        base_name = os.path.basename(self.image_path)
        debug_path = os.path.join(debug_dir, f"preprocessed_{base_name}")
        cv2.imwrite(debug_path, binary)
        
        return binary
    
    def detect_classes(self, preprocessed_image):
        """Detect class boxes in the UML diagram."""
        # Create a copy of the image for visualization
        debug_image = cv2.cvtColor(preprocessed_image, cv2.COLOR_GRAY2BGR)
        
        # Find contours in the binary image - use RETR_TREE to get hierarchy
        contours, hierarchy = cv2.findContours(
            preprocessed_image, 
            cv2.RETR_TREE, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Get image dimensions
        height, width = preprocessed_image.shape
        min_box_width = width * 0.1  # Minimum 10% of image width
        min_box_height = height * 0.05  # Minimum 5% of image height
        
        # Filter contours by size and shape to find potential class boxes
        class_boxes = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            # Area of the contour
            area = cv2.contourArea(contour)
            # Perimeter of the contour
            perimeter = cv2.arcLength(contour, True)
            # Approximate the contour to a polygon
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # Filter by size
            if w < min_box_width or h < min_box_height:
                continue
                
            # Filter by shape - rectangles have 4 vertices
            if len(approx) == 4:
                # Check if it's a rectangular shape (not too skewed)
                aspect_ratio = w / h
                if 0.3 <= aspect_ratio <= 3.0:
                    # Draw contour on debug image
                    cv2.drawContours(debug_image, [contour], 0, (0, 0, 255), 2)
                    cv2.putText(
                        debug_image, 
                        f"{i}", 
                        (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, 
                        (0, 0, 255), 
                        1
                    )
                    
                    # Add to class boxes
                    class_boxes.append((x, y, w, h))
        
        # Save the debug image
        debug_dir = os.path.join(os.path.dirname(self.image_path), "debug")
        os.makedirs(debug_dir, exist_ok=True)
        base_name = os.path.basename(self.image_path)
        debug_path = os.path.join(debug_dir, f"boxes_{base_name}")
        cv2.imwrite(debug_path, debug_image)
        
        # If we didn't find any boxes using contour approximation,
        # try with fixed grid-based approach
        if not class_boxes:
            print("No class boxes found with contour detection, trying grid approach...")
            
            # Divide the image into a grid of potential boxes
            grid_cols = 3
            grid_rows = 3
            cell_width = width // grid_cols
            cell_height = height // grid_rows
            
            for row in range(grid_rows):
                for col in range(grid_cols):
                    x = col * cell_width
                    y = row * cell_height
                    w = cell_width
                    h = cell_height
                    
                    # Draw grid cell on debug image
                    cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 1)
                    
                    # Add to class boxes
                    class_boxes.append((x, y, w, h))
            
            # Save the grid debug image
            grid_debug_path = os.path.join(debug_dir, f"grid_{base_name}")
            cv2.imwrite(grid_debug_path, debug_image)
        
        return class_boxes
    
    def extract_text_from_region(self, region):
        """Extract text from a specific region using OCR."""
        x, y, w, h = region
        roi = self.image[y:y+h, x:x+w]
        
        # Convert ROI to grayscale for OCR
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Preprocess the ROI for better OCR results
        # Apply adaptive thresholding
        binary_roi = cv2.adaptiveThreshold(
            gray_roi, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 
            2
        )
        
        # Resize the ROI (making it larger often helps OCR)
        scale_factor = 2
        resized_roi = cv2.resize(
            binary_roi, 
            None, 
            fx=scale_factor, 
            fy=scale_factor, 
            interpolation=cv2.INTER_CUBIC
        )
        
        # Save the region for debugging
        debug_dir = os.path.join(os.path.dirname(self.image_path), "debug")
        os.makedirs(debug_dir, exist_ok=True)
        debug_path = os.path.join(debug_dir, f"region_{x}_{y}_{w}_{h}.png")
        cv2.imwrite(debug_path, resized_roi)
        
        # Configure Tesseract parameters for better results
        custom_config = r'--oem 3 --psm 6 -l eng'
        
        # Use Tesseract to extract text
        text = pytesseract.image_to_string(resized_roi, config=custom_config)
        
        return text.strip()
    
    def parse_class_text(self, text):
        """Parse extracted text into class components (name, attributes, methods)."""
        # Print raw text for debugging
        print(f"Raw extracted text:\n{text}\n---")
        
        lines = text.strip().split('\n')
        if not lines:
            return {
                'name': "",
                'attributes': [],
                'methods': []
            }
        
        # First line is typically the class name
        # Remove common OCR artifacts and clean up
        class_name = lines[0].strip()
        class_name = re.sub(r'[^a-zA-Z0-9_<>]', '', class_name)
        
        # Clean up common OCR errors
        class_name = class_name.replace('oa0', 'oa')
        class_name = class_name.replace('0a', 'oa')
        
        # Look for oa* class names which are common in OpenAccess
        oa_match = re.search(r'(oa[A-Z][a-zA-Z0-9_]*)', class_name)
        if oa_match:
            class_name = oa_match.group(1)
        
        attributes = []
        methods = []
        
        # Track where we are in the class diagram
        section = "name"  # Start in the name section
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            # Section separators are often horizontal lines in UML,
            # which OCR might interpret as dashes or underscores
            if re.match(r'^[-_=]{3,}$', line):
                # Move to the next section
                if section == "name":
                    section = "attributes"
                elif section == "attributes":
                    section = "methods"
                continue
            
            # Process based on current section
            if section == "attributes":
                # Clean up the attribute line
                attr_line = re.sub(r'\s+', ' ', line)
                attributes.append(attr_line)
            elif section == "methods":
                # Clean up the method line
                method_line = re.sub(r'\s+', ' ', line)
                methods.append(method_line)
            
        # If we didn't find sections based on separators, try content-based detection
        if not attributes and not methods:
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                # Methods typically have parentheses
                if '(' in line:
                    methods.append(line)
                # Attributes often have colons or types
                elif ':' in line or re.search(r'[a-zA-Z]+\s+[a-zA-Z]+', line):
                    attributes.append(line)
        
        return {
            'name': class_name,
            'attributes': attributes,
            'methods': methods
        }
    
    def parse_relationships(self, class_boxes):
        """Attempt to identify relationships between classes."""
        # This is a complex task requiring advanced image processing
        # For now, we'll return a placeholder
        relationships = []
        
        # Future implementation would detect lines between class boxes
        # and determine relationship types
        
        return relationships
    
    def parse(self):
        """Parse the UML diagram and return structured data."""
        # Preprocess the image
        preprocessed = self.preprocess_image()
        
        # Detect class boxes
        class_boxes = self.detect_classes(preprocessed)
        
        # Extract class information
        classes = []
        for box in class_boxes:
            text = self.extract_text_from_region(box)
            class_info = self.parse_class_text(text)
            class_info['position'] = box  # Save position for relationship detection
            classes.append(class_info)
        
        # Detect relationships
        relationships = self.parse_relationships(class_boxes)
        
        # Create the final UML structure
        uml_structure = {
            'classes': [
                {k: v for k, v in c.items() if k != 'position'} 
                for c in classes
            ],
            'relationships': relationships
        }
        
        return uml_structure
    
    def save_as_yaml(self, output_path):
        """Parse the UML diagram and save as YAML."""
        uml_structure = self.parse()
        
        with open(output_path, 'w') as f:
            yaml.dump(uml_structure, f, default_flow_style=False)
        
        print(f"UML structure saved to {output_path}")
        return uml_structure

def main():
    """Main function to run the UML parser."""
    parser = argparse.ArgumentParser(description='Parse UML diagrams to YAML')
    parser.add_argument('image_path', help='Path to the UML diagram image')
    parser.add_argument(
        '-o', '--output', 
        help='Output YAML file path (default: same as input with .yaml extension)'
    )
    
    args = parser.parse_args()
    
    try:
        # Set default output path if not provided
        output_path = args.output
        if not output_path:
            input_path = Path(args.image_path)
            output_path = str(input_path.with_suffix('.yaml'))
        
        # Parse the UML diagram
        uml_parser = UMLParser(args.image_path)
        uml_structure = uml_parser.save_as_yaml(output_path)
        
        # Print a summary
        class_count = len(uml_structure['classes'])
        relationship_count = len(uml_structure['relationships'])
        print(f"Parsed {class_count} classes and {relationship_count} relationships")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()