# file_reader.py
import textwrap
import logging
from enum import Enum
from logging_setup import setup_logging

# Set up logging using the imported function
setup_logging(log_level=logging.INFO)


def pretty_print(text):
    """
    Formats and pretty prints the given text by handling newlines and wrapping text.

    :param text: The text to format and pretty print.
    :return: The formatted text as a string.
    """
    # Use textwrap.fill to format the text to a width of 80 characters per line
    formatted_text = textwrap.fill(text, width=80, replace_whitespace=False)
    return formatted_text

def read_file_contents(file_name):
    """
    Reads the contents of a local text file and returns it as a string.
    Handles exceptions for file not found and other errors.

    :param file_name: The name of the file to read.
    :return: The contents of the file as a string, or an error message if an exception occurs.
    """
    try:
        # Attempt to open and read the specified file
        with open(file_name, 'r') as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        # Handle the case where the file does not exist
        error_message = f"Error: The file {file_name} was not found."
        logging.error(error_message)
        return error_message
    except Exception as e:
        # Handle any other exceptions that may occur during file reading
        error_message = f"Error: An error occurred while reading the file {file_name}. Details: {e}"
        logging.error(error_message)
        return error_message

def create_complete_prompt(template_file, content_file):
    """
    Reads the prompt template and content files, replaces the variables in the template with the content,
    and returns the complete prompt.

    :param template_file: The file name of the prompt template.
    :param content_file: The file name of the content to replace in the template.
    :return: The complete prompt as a string, or an error message if file reading fails.
    """
    # Read the prompt template and content files
    template = read_file_contents(template_file)
    content = read_file_contents(content_file)
    
    # Check if there were errors reading the files
    if template.startswith("Error:") or content.startswith("Error:"):
        # If either file read resulted in an error, return the error messages
        error_message = f"Template file error: {template}\nContent file error: {content}"
        logging.error(error_message)
        return error_message
    
    # Replace the placeholder in the template with the actual content
    try:
        complete_prompt = template.replace("{{log_entry}}", content)
        logging.info(f"Prompt successfully created using template {template_file} and content {content_file}")
        print(complete_prompt)  # Optional: print the complete prompt for debugging purposes
        return complete_prompt
    except Exception as e:
        # Handle any exceptions that may occur during the placeholder replacement
        error_message = f"Error: An error occurred while creating the prompt. Details: {e}"
        logging.error(error_message)
        return error_message
