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
        
        # Apply thresholding to get a binary image
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Perform morphological operations to remove noise
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=1)
        binary = cv2.erode(binary, kernel, iterations=1)
        
        return binary
    
    def detect_classes(self, preprocessed_image):
        """Detect class boxes in the UML diagram."""
        # Find contours in the binary image
        contours, _ = cv2.findContours(
            preprocessed_image, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by size and shape to find potential class boxes
        class_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio and minimum size
            aspect_ratio = w / h
            if 0.5 <= aspect_ratio <= 2.0 and w > 100 and h > 50:
                class_boxes.append((x, y, w, h))
        
        return class_boxes
    
    def extract_text_from_region(self, region):
        """Extract text from a specific region using OCR."""
        x, y, w, h = region
        roi = self.image[y:y+h, x:x+w]
        
        # Convert ROI to grayscale for OCR
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Use Tesseract to extract text
        text = pytesseract.image_to_string(gray_roi)
        return text.strip()
    
    def parse_class_text(self, text):
        """Parse extracted text into class components (name, attributes, methods)."""
        # Basic parsing logic - can be improved
        lines = text.strip().split('\n')
        
        class_name = lines[0] if lines else ""
        attributes = []
        methods = []
        
        # Simple heuristic: lines with ':' are likely attributes or methods
        # lines with '(' are likely methods
        for line in lines[1:]:
            if '(' in line:
                methods.append(line.strip())
            elif ':' in line:
                attributes.append(line.strip())
        
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