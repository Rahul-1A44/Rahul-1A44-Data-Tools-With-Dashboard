import json
import yaml
import csv
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import xml.etree.ElementTree as ET
from reportlab.lib.utils import simpleSplit
from PyPDF2 import PdfReader
import openpyxl


def convert_data(input_content, input_format, output_format):
    """
    Converts input data from one format to another.
    Handles various text-based and binary inputs/outputs.

    Args:
        input_content: The data to convert. Can be bytes (for file uploads),
                       a string (for text area input), or a Python object
                       (e.g., from web scraping).
        input_format (str): The format of the input_content (e.g., 'json', 'csv',
                            'text', 'python_object', 'xml', 'yaml', 'xlsx', 'pdf').
        output_format (str): The desired output format (e.g., 'json', 'csv',
                             'text', 'pdf', 'xlsx', 'xml', 'yaml').

    Returns:
        dict: A dictionary containing 'converted_data' (bytes or string) and
              'is_binary' (boolean), or an 'error' message if conversion fails.
    """
    data = None
    is_binary_output = False

    
    try:
        if input_format == 'json':
            if isinstance(input_content, bytes):
                input_content = input_content.decode('utf-8')
            data = json.loads(input_content)

        elif input_format == 'yaml':
            if isinstance(input_content, bytes):
                input_content = input_content.decode('utf-8')
            data = yaml.safe_load(input_content)

        elif input_format == 'csv':
            if isinstance(input_content, bytes):
                input_content = input_content.decode('utf-8')
            
            df = pd.read_csv(io.StringIO(input_content))
            data = df.to_dict(orient='records')

        elif input_format == 'xml':
            if isinstance(input_content, bytes):
                input_content = input_content.decode('utf-8')
            root = ET.fromstring(input_content)
            
            # Simplified XML parsing for basic structures
            data = {root.tag: {child.tag: child.text for child in root}}
            if not data[root.tag]: # If no children, take root text
                data = {root.tag: root.text}

        elif input_format == 'text':
            if isinstance(input_content, bytes):
                input_content = input_content.decode('utf-8')
            
            data = {"content": input_content}

        elif input_format == 'xlsx':
            # Handle both file paths (string) and file content (bytes)
            if isinstance(input_content, str): 
                df = pd.read_excel(input_content)
            else: 
                df = pd.read_excel(io.BytesIO(input_content))
            data = df.to_dict(orient='records')

        elif input_format == 'pdf':
            # Handle both file paths (string) and file content (bytes)
            if isinstance(input_content, str): 
                with open(input_content, 'rb') as pdf_file:
                    reader = PdfReader(pdf_file)
                    pdf_text = [page.extract_text() for page in reader.pages if page.extract_text()]
                    data = "\n".join(pdf_text)
            else: 
                pdf_file = io.BytesIO(input_content)
                reader = PdfReader(pdf_file)
                pdf_text = [page.extract_text() for page in reader.pages if page.extract_text()]
                data = "\n".join(pdf_text)
            

        elif input_format == 'python_object':
            
            data = input_content

        else:
            return {'error': f"Unsupported input format: {input_format}"}

        if data is None:
            return {'error': "Could not parse input data or input was empty."}

    except (json.JSONDecodeError, yaml.YAMLError, pd.errors.EmptyDataError, ET.ParseError, Exception) as e:
        return {'error': f"Error parsing input {input_format} data: {e}"}

    
    try:
        converted_data = None

        if output_format == 'json':
            converted_data = json.dumps(data, indent=2)

        elif output_format == 'yaml':
            converted_data = yaml.dump(data, indent=2, sort_keys=False)

        elif output_format == 'csv':
            output_buffer = io.StringIO()
            df = _convert_to_dataframe(data)
            df.to_csv(output_buffer, index=False)
            converted_data = output_buffer.getvalue()

        elif output_format == 'xml':
            root = ET.Element("root")
            if isinstance(data, list):
                for i, item in enumerate(data):
                    # Use a generic 'item' tag for list elements for consistency
                    elem = ET.SubElement(root, "item")
                    _dict_to_xml_elements(elem, item)
            elif isinstance(data, dict):
                _dict_to_xml_elements(root, data)
            else:
                # For non-dict/list data, wrap in a generic 'content' tag
                generic_element = ET.SubElement(root, "content")
                generic_element.text = str(data)

            # pretty_print is already set to True in the original code
            converted_data = ET.tostring(root, encoding='unicode', pretty_print=True)

        elif output_format == 'text':
            # If data was originally from 'text' input, return its content
            if isinstance(data, dict) and 'content' in data:
                converted_data = data['content']
            elif isinstance(data, list) and all(isinstance(i, dict) and 'content' in i for i in data): 
                converted_data = "\n".join([item["content"] for item in data])
            elif isinstance(data, (dict, list)):
                # Fallback to JSON string for other dict/list structures
                converted_data = json.dumps(data, indent=2) 
            else:
                converted_data = str(data) 

        elif output_format == 'pdf':
            is_binary_output = True
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            # Use the updated helper function for cleaner PDF text extraction
            text_content = _get_text_for_pdf(data) 

            lines = text_content.split('\n')
            y_position = 750
            line_height = 14
            margin_left = 50
            page_width = letter[0]
            drawable_width = page_width - (2 * margin_left) 
            
            font_size = 10

            p.setFont('Helvetica', font_size)

            for line in lines:
                wrapped_lines = simpleSplit(line, 'Helvetica', font_size, drawable_width)
                for wrapped_line in wrapped_lines:
                    if y_position < 50: # Check if new page is needed
                        p.showPage()
                        p.setFont('Helvetica', font_size)
                        y_position = 750 # Reset Y position for new page

                    try:
                        p.drawString(margin_left, y_position, wrapped_line)
                    except Exception:
                        # Fallback for characters not supported by the font
                        safe_line = ''.join(char if ord(char) < 128 else '?' for char in wrapped_line)
                        p.drawString(margin_left, y_position, safe_line)

                    y_position -= line_height 

            p.save()
            converted_data = buffer.getvalue()
            buffer.close()

        elif output_format == 'xlsx':
            is_binary_output = True
            output_buffer = BytesIO()
            df = _convert_to_dataframe(data)
            df.to_excel(output_buffer, index=False, engine='openpyxl')
            converted_data = output_buffer.getvalue()
            output_buffer.close()

        else:
            return {'error': f"Unsupported output format: {output_format}"}

    except Exception as e:
        return {'error': f"Error converting data to {output_format}: {e}"}

    return {'converted_data': converted_data, 'is_binary': is_binary_output}


def _convert_to_dataframe(data):
    """Converts various data types into a pandas DataFrame."""
    if isinstance(data, list) and all(isinstance(i, dict) for i in data):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        return pd.DataFrame([data])
    elif isinstance(data, str):
        lines = data.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip()]
        return pd.DataFrame({'Line_Number': range(1, len(clean_lines) + 1), 'Content': clean_lines})
    else:
        # Fallback for other data types
        text_content = str(data)
        lines = text_content.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip()]
        return pd.DataFrame({'Line_Number': range(1, len(clean_lines) + 1), 'Content': clean_lines})


def _get_text_for_pdf(data):
    """
    Extracts suitable text content from various data types for PDF output.
    Prioritizes tabular representation for structured data.
    """
    if isinstance(data, dict) and 'content' in data:
        return data['content']
    elif isinstance(data, list) and all(isinstance(i, dict) and 'content' in i for i in data):
        # If it's a list of dicts with 'content' keys, join them
        return "\n".join([item["content"] for item in data])
    elif isinstance(data, (list, dict)):
        # Attempt to convert to DataFrame for better tabular representation
        try:
            df = _convert_to_dataframe(data)
            # Use to_string() for a readable table-like output, without index
            return df.to_string(index=False)
        except Exception:
            # Fallback to JSON dump if conversion to DataFrame for string representation fails
            return json.dumps(data, indent=2)
    else:
        # For simple types, just convert to string
        return str(data)


def _dict_to_xml_elements(parent, data):
    """Recursively converts a dictionary to XML elements."""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                element = ET.SubElement(parent, key)
                _dict_to_xml_elements(element, value)
            else:
                element = ET.SubElement(parent, key)
                element.text = str(value)
    elif isinstance(data, list):
        for item in data:
            # Always use a generic "item" tag for list elements in XML
            element = ET.SubElement(parent, "item")
            _dict_to_xml_elements(element, item)
    else:
        # If data is a simple type, set it as text of the parent element
        parent.text = str(data)
