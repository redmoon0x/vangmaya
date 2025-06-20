from dotenv import load_dotenv
from gradio_interface import create_interface

# Load environment variables from .env file
load_dotenv()

# Create and launch the interface
demo = create_interface()
demo.launch()
