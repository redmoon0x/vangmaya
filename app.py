from gradio_interface import create_interface

# Create and launch the interface
demo = create_interface()
demo.launch(server_name="0.0.0.0")
