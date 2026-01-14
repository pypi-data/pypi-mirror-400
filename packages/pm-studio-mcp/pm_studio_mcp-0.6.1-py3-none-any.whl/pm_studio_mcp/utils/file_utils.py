import os
import csv
from typing import List
import re
import glob
import shutil
# Optional import for markitdown - will also be imported locally when needed
try:
    from markitdown import MarkItDown
except ImportError:
    # Module will be imported when needed in the function
    pass
# Stop words

class FileUtils:
    @staticmethod
    def replace_stop_words(text: str) -> str:
        """Replace stop words with asterisks."""
        STOP_WORDS = ['fuck', 'shit', 'damn', 'ass', 'bitch', 'crap']

        if not text:
            return text
        
        result = text
        for word in STOP_WORDS:
            pattern = r'\b' + word + r'\b'
            result = re.sub(pattern, '***', result, flags=re.IGNORECASE)
        
        return result

    @staticmethod
    def generate_markdown_tool(content: str, filename: str, working_path: str):
        """
        Write the given content to a Markdown file in the working directory with a customizable filename.
                
        Args:
            content (str): The content to write to the Markdown file.
            filename (str, optional): The name of the output file.
                
        Returns:
            str: Path to the saved Markdown file.
        """
        try:
            # Ensure the filename has .md extension
            if not filename.endswith('.md'):
                filename = f"{filename}.md"
                
            # Define the output file path
            output_file = os.path.join(working_path, filename)
                    
            # Write content to the file
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(content)
                    
            return f"Content successfully written to {output_file}"
        except Exception as e:
            return f"Error writing to markdown file: {str(e)}"
        
    @staticmethod
    def upload_files_to_working_dir_tool(file_paths: List[str], working_path): #handle the file uploaded from the client
        """
        Copies the CSV files uploaded from the client chat to the working directory and renames them with an "_intermediate" suffix.

        Args:
            file_paths (List[str]): List of file paths uploaded from the client chat.
        """
        copied_files = []
        for file_path in file_paths:
            try:
                # Ensure the file is a CSV file
                if not file_path.lower().endswith('.csv'):
                    return f"Error: Only CSV files are allowed. Invalid file: {file_path}"

                # Add "_intermediate" suffix to the file name
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                destination = os.path.join(working_path, f"{base_name}_intermediate.csv")

                # Copy the file to the working directory
                shutil.copy(file_path, destination)
                copied_files.append(destination)
            except Exception as e:
                return f"Error copying file {file_path}: {str(e)}"

        return f"Copied {len(copied_files)} files to working directory: {', '.join(copied_files)}"
    
    @staticmethod
    def convert_to_markdown_tool(file_path: str, working_path: str):
        """
        Convert a document (doc/excel/ppt/pdf/images/csv/json/xml) to markdown format using MarkItDown.

        Args:
            file_path (str): Path to the input document file
            working_path (str): Path to the working directory to save output

        Returns:
            str: Path to the generated markdown file or error message
        """
        try:
            # Import here to avoid circular imports
            from markitdown import MarkItDown
            
            md = MarkItDown()
            result = md.convert(file_path)
            
            # Generate output filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(working_path, f"{base_name}.md")
            
            # Write the converted content to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
                
            return f"File converted successfully: {output_file}"
        except Exception as e:
            return f"Error converting file: {str(e)}"