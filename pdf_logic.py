import os
import io
from pypdf import PdfReader, PdfWriter

def split_pdf(input_stream, max_size_mb):
    """
    Splits a PDF from an input stream into multiple parts based on size.
    Returns a list of tuples (filename, byte_content).
    """
    reader = PdfReader(input_stream)
    total_pages = len(reader.pages)
    max_size_bytes = max_size_mb * 1024 * 1024
    safety_factor = 0.9
    
    parts = []
    current_writer = PdfWriter()
    current_pages = []
    current_size = 0
    part_num = 1
    
    for page_idx in range(total_pages):
        # Calculate size of current page
        temp_writer = PdfWriter()
        temp_writer.add_page(reader.pages[page_idx])
        
        buffer = io.BytesIO()
        temp_writer.write(buffer)
        page_size = len(buffer.getvalue())
        
        # Check if we should start a new part
        if (current_size + page_size > max_size_bytes * safety_factor 
            and current_pages):
            # Save current part
            output_buffer = io.BytesIO()
            current_writer.write(output_buffer)
            parts.append((f"parte_{part_num:03d}.pdf", output_buffer.getvalue()))
            
            # Reset for next part
            current_writer = PdfWriter()
            current_pages = []
            current_size = 0
            part_num += 1
        
        # Add page to current part
        current_writer.add_page(reader.pages[page_idx])
        current_pages.append(page_idx)
        current_size += page_size
    
    # Add last part
    if current_pages:
        output_buffer = io.BytesIO()
        current_writer.write(output_buffer)
        parts.append((f"parte_{part_num:03d}.pdf", output_buffer.getvalue()))
        
    return parts
