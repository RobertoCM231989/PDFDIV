import os
import io
from pypdf import PdfReader, PdfWriter

def split_pdf(input_stream, max_size_mb):
    """
    ULTRA-OPTIMIZED PDF Splitter.
    Minimizes costly PDF writing operations by estimating page sizes
    and using aggressive chunking.
    """
    reader = PdfReader(input_stream)
    total_pages = len(reader.pages)
    max_size_bytes = max_size_mb * 1024 * 1024
    safety_factor = 0.96
    
    parts = []
    current_writer = PdfWriter()
    current_pages = []
    
    # 1. Estimation Phase: Get total file size to estimate avg page size
    input_stream.seek(0, os.SEEK_END)
    total_file_size = input_stream.tell()
    input_stream.seek(0)
    avg_page_size = total_file_size / total_pages if total_pages > 0 else 0
    
    # 2. Adaptive Chunking:
    # If avg page is 100KB and limit is 4MB, we can safely jump ~30 pages.
    # We use a conservative multiplier of 0.5 for the jump.
    jump_size = max(1, int((max_size_bytes / (avg_page_size + 1)) * 0.4))
    
    i = 0
    part_num = 1
    
    while i < total_pages:
        # Determine how many pages to add in this batch
        remaining_in_part = total_pages - i
        batch_size = min(jump_size, remaining_in_part)
        
        # Add the batch
        for _ in range(batch_size):
            current_writer.add_page(reader.pages[i])
            current_pages.append(i)
            i += 1
            
        # Check size only after the batch
        buffer = io.BytesIO()
        current_writer.write(buffer)
        current_size = len(buffer.getvalue())
        
        # If we went over, we backtrack only ONE batch and then go one by one
        if current_size > max_size_bytes * safety_factor:
            # Backtrack index
            i -= batch_size
            # Rebuild writer minus the last batch
            current_writer = PdfWriter()
            for _ in range(len(current_pages) - batch_size):
                p_idx = current_pages.pop(0) # Keep older pages
                current_writer.add_page(reader.pages[p_idx])
            
            # Now add one by one until it hits the limit
            # This is the "safe" fallthrough
            while i < total_pages:
                current_writer.add_page(reader.pages[i])
                
                temp_buffer = io.BytesIO()
                current_writer.write(temp_buffer)
                if len(temp_buffer.getvalue()) > max_size_bytes * safety_factor:
                    # The page at 'i' made it too big.
                    # Send what we have (if any)
                    if len(current_pages) > 0:
                        parts.append((f"parte_{part_num:03d}.pdf", final_content))
                        part_num += 1
                        current_writer = PdfWriter()
                        current_pages = []
                        # Note: we DON'T increment 'i' because this page goes to next part
                        break
                    else:
                        # Single page is bigger than limit - accept it and move on
                        parts.append((f"parte_{part_num:03d}.pdf", temp_buffer.getvalue()))
                        part_num += 1
                        current_writer = PdfWriter()
                        current_pages = []
                        i += 1
                        break
                
                final_content = temp_buffer.getvalue()
                current_pages.append(i)
                i += 1
        
        # If we reached the end of the batch and we are still fine, 
        # but it's the end of the PDF
        elif i == total_pages:
            parts.append((f"parte_{part_num:03d}.pdf", buffer.getvalue()))
            
    return parts
