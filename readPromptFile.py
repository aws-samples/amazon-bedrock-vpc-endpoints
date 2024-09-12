import logging

# Set up logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')

# Create and configure a file handler to log messages to a file named 'invoke.log'
file_handler = logging.FileHandler('invoke.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def read_file_contents(filename):
    """
    Reads the contents of a file.
    Args:
        filename (str): The path to the file.
    Returns:
        str: The contents of the file as a string, or an error message if an exception occurs.
    """
    try:
        # Open and read the file
        with open(filename, 'r') as f:
            file_contents = f.read()
        logger.info(f"File '{filename}' read successfully.")
        return file_contents
    except FileNotFoundError:
        # Handle the case where the file does not exist
        error_message = f"Error: The file '{filename}' was not found."
        logger.error(error_message)
        return error_message
    except Exception as e:
        # Handle any other exceptions that may occur
        error_message = f"Error: An error occurred while reading the file '{filename}'. Details: {e}"
        logger.error(error_message)
        return error_message

# Uncomment the code below to use this module independently for testing purposes
'''
if __name__ == '__main__':
    # Example usage of read_file_contents function
    filename = 'prompt.txt'

    # Attempt to read the contents of the specified file
    file_contents = read_file_contents(filename)

    # Print the contents or error message to the console
    print(file_contents)
'''
