import logging
import PyPDF2
from typing import List, Dict, Optional

class PDFProcessor:
    """
    A class for processing PDF documents and extracting structured information.
    This extends the basic functionality in the DocumentProcessor class.
    """
    
    def __init__(self, pdf_path: str):
        """Initialize with the path to a PDF file."""
        self.pdf_path = pdf_path
        self.text_content = ""
        self.pages = []
        self.metadata = {}
        
        logging.info(f"Initializing PDFProcessor for {pdf_path}")
        self._load_pdf()
    
    def _load_pdf(self) -> None:
        """Load the PDF and extract text and metadata."""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                self.metadata = {
                    "page_count": len(reader.pages),
                    "title": reader.metadata.title if reader.metadata.title else "Unknown",
                    "author": reader.metadata.author if reader.metadata.author else "Unknown",
                    "subject": reader.metadata.subject if reader.metadata.subject else "Unknown",
                    "creator": reader.metadata.creator if reader.metadata.creator else "Unknown"
                }
                
                # Extract text from each page
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    self.pages.append(page_text)
                    self.text_content += page_text + "\n\n"
                
                logging.info(f"Successfully loaded PDF with {len(self.pages)} pages")
        
        except Exception as e:
            logging.error(f"Error loading PDF {self.pdf_path}: {e}")
            raise
    
    def get_full_text(self) -> str:
        """Return the full text content of the PDF."""
        return self.text_content
    
    def get_page(self, page_num: int) -> Optional[str]:
        """Return the text content of a specific page (0-indexed)."""
        if 0 <= page_num < len(self.pages):
            return self.pages[page_num]
        else:
            logging.warning(f"Page {page_num} out of range (0-{len(self.pages)-1})")
            return None
    
    def get_metadata(self) -> Dict:
        """Return the PDF metadata."""
        return self.metadata
    
    def extract_sections(self, section_markers: List[str] = None) -> Dict[str, str]:
        """
        Extract sections from the PDF based on section markers.
        If no markers are provided, tries to identify sections based on common patterns.
        """
        if not section_markers:
            # Default section markers for common document structures
            section_markers = [
                "Introduction", "Overview", "Background", 
                "Method", "Results", "Discussion", "Conclusion",
                "References", "Appendix"
            ]
        
        sections = {}
        current_section = "Header"
        current_content = []
        
        # Process line by line
        for line in self.text_content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_section_header = False
            for marker in section_markers:
                if line.lower().startswith(marker.lower()) or line.lower() == marker.lower():
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = line
                    current_content = []
                    is_section_header = True
                    break
            
            if not is_section_header:
                current_content.append(line)
        
        # Save the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        logging.info(f"Extracted {len(sections)} sections from PDF")
        return sections
    
    def extract_qa_pairs(self) -> List[Dict[str, str]]:
        """
        Attempt to extract question-answer pairs from the document.
        This is useful for FAQ-type documents.
        """
        qa_pairs = []
        lines = self.text_content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for question patterns
            if line.endswith('?') or (line.startswith('Q:') or line.startswith('Question:')):
                question = line
                answer_lines = []
                
                # Look for the answer in subsequent lines
                j = i + 1
                while j < len(lines) and not (lines[j].strip().endswith('?') or 
                                             lines[j].strip().startswith('Q:') or 
                                             lines[j].strip().startswith('Question:')):
                    if lines[j].strip():  # Skip empty lines
                        answer_lines.append(lines[j].strip())
                    j += 1
                
                if answer_lines:
                    answer = ' '.join(answer_lines)
                    qa_pairs.append({
                        "question": question,
                        "answer": answer
                    })
                
                i = j - 1  # Move to the line before the next question
            
            i += 1
        
        logging.info(f"Extracted {len(qa_pairs)} QA pairs from PDF")
        return qa_pairs

# Example usage
if __name__ == "__main__":
    # This is just for demonstration
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        processor = PDFProcessor(pdf_path)
        
        print(f"PDF Metadata: {processor.get_metadata()}")
        print(f"First page content: {processor.get_page(0)[:200]}...")
        
        sections = processor.extract_sections()
        print(f"Extracted {len(sections)} sections")
        
        qa_pairs = processor.extract_qa_pairs()
        print(f"Extracted {len(qa_pairs)} QA pairs")
    else:
        print("Please provide a PDF file path as an argument") 