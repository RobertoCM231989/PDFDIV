import os
import io
import fitz  # PyMuPDF

def split_pdf(input_stream, max_size_mb, progress_callback=None):
    """
    Split PDF using PyMuPDF (fitz) - significantly faster than pypdf.
    """
    if progress_callback:
        progress_callback(0)
        
    print(f"DEBUG: Starting split_pdf with max_size_mb={max_size_mb}")
    
    # Load PDF from stream
    doc = fitz.open(stream=input_stream, filetype="pdf")
    total_pages = len(doc)
    max_size_bytes = max_size_mb * 1024 * 1024
    safety_factor = 0.95
    
    parts = []
    current_doc = fitz.open()
    part_num = 1
    
    print(f"DEBUG: PDF has {total_pages} pages")
    
    for i in range(total_pages):
        # Add page to current part
        current_doc.insert_pdf(doc, from_page=i, to_page=i)
        
        # Report progress
        if progress_callback:
            percent = int(((i + 1) / total_pages) * 100)
            progress_callback(percent)
        
        # Check size periodically (every 5 pages or at the end)
        if (i + 1) % 5 == 0 or i == total_pages - 1:
            buffer = current_doc.tobytes()
            current_size = len(buffer)
            
            # If over limit, backtrack
            if current_size > max_size_bytes * safety_factor:
                # If it's just one page and it's over, we must send it
                if len(current_doc) > 1:
                    # Remove the last 5 pages added and do them one by one
                    # Simplified logic for fast response:
                    # Actually, PyMuPDF is so fast we can just check more often
                    # or do a more precise split.
                    
                    # Backtrack: Rebuild part without the last batch
                    # But let's keep it simple: just close this part BEFORE the batch
                    # if the batch makes it too big.
                    
                    # More precise: remove pages until it fits
                    while len(current_doc) > 1 and len(buffer) > max_size_bytes * safety_factor:
                        current_doc.delete_page(len(current_doc) - 1)
                        buffer = current_doc.tobytes()
                        i -= 1 # Return index to process these pages in the next part
                    
                    parts.append((f"parte_{part_num:03d}.pdf", buffer))
                    print(f"DEBUG: Saved part {part_num} with {len(current_doc)} pages")
                    part_num += 1
                    current_doc = fitz.open()
                else:
                    # Single big page
                    parts.append((f"parte_{part_num:03d}.pdf", buffer))
                    print(f"DEBUG: Saved part {part_num} (single page)")
                    part_num += 1
                    current_doc = fitz.open()
            
            elif i == total_pages - 1:
                # Final part
                parts.append((f"parte_{part_num:03d}.pdf", buffer))
                print(f"DEBUG: Saved final part {part_num}")

    doc.close()
    print(f"DEBUG: Completed splitting into {len(parts)} parts")
    return parts
