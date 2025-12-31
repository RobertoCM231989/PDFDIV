import os
import io
from pypdf import PdfReader, PdfWriter

def split_pdf(input_stream, max_size_mb):
    """
    Optimized PDF splitter. Splits a PDF based on size.
    Uses chunked processing to avoid calculating the size of EVERY page individually,
    which is the main bottleneck.
    """
    reader = PdfReader(input_stream)
    total_pages = len(reader.pages)
    max_size_bytes = max_size_mb * 1024 * 1024
    safety_factor = 0.95  # Slightly higher safety factor for optimized logic
    
    parts = []
    current_writer = PdfWriter()
    current_pages = []
    part_num = 1
    
    # Heuristic: start with a safe chunk size based on average page size
    # If file is 100MB and 100 pages, avg is 1MB. Max is 4MB. 
    # We can probably jump 2-3 pages safely.
    
    i = 0
    while i < total_pages:
        # Add a page
        current_writer.add_page(reader.pages[i])
        current_pages.append(i)
        
        # Periodically check size (every 5 pages or if it's the last page)
        # Checking size of the WHOLE writer is faster than checking individual pages
        # because of shared resources in PDFs.
        if len(current_pages) % 5 == 0 or i == total_pages - 1:
            buffer = io.BytesIO()
            current_writer.write(buffer)
            current_size = len(buffer.getvalue())
            
            # If we exceeded the limit, we need to backtrack and find the exact split point
            if current_size > max_size_bytes * safety_factor:
                # If we only added ONE page in this step and it already exceeded, 
                # we have to include it (unless it's truly massive, but we can't split a page)
                # or split before it if we have previous pages.
                
                if len(current_pages) > 1:
                    # Remove the last pages added in this chunk until we are under the limit
                    # or only 1 page remains.
                    while len(current_pages) > 1:
                        # Re-calculate size without the last page
                        # (Unfortunately pypdf doesn't support easy page removal, 
                        # so we rebuild the part minus the last page)
                        last_page = current_pages.pop()
                        i -= 1 # Move the index back
                        
                        temp_writer = PdfWriter()
                        for p in current_pages:
                            temp_writer.add_page(reader.pages[p])
                        
                        temp_buffer = io.BytesIO()
                        temp_writer.write(temp_buffer)
                        if len(temp_buffer.getvalue()) <= max_size_bytes * safety_factor:
                            # We found the split point!
                            current_writer = temp_writer
                            final_content = temp_buffer.getvalue()
                            parts.append((f"parte_{part_num:03d}.pdf", final_content))
                            
                            # Reset for next part
                            current_writer = PdfWriter()
                            current_pages = []
                            part_num += 1
                            break
                    else:
                        # If we are here, even the first page of the chunk might be too big
                        # or it's the only page left. We must split here.
                        # We keep the current page as the only page in the part if it was the first.
                        # Wait, the logic above resets 'i', so we are safe.
                        pass
                else:
                    # Single page exceeds limit. We accept it as a single part.
                    parts.append((f"parte_{part_num:03d}.pdf", buffer.getvalue()))
                    current_writer = PdfWriter()
                    current_pages = []
                    part_num += 1
            
            elif i == total_pages - 1:
                # End of document, save last part
                parts.append((f"parte_{part_num:03d}.pdf", buffer.getvalue()))
                
        i += 1
        
    return parts
