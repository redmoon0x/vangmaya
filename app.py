from voxlingo import VoxLingo

# Create the VoxLingo application
voxlingo = VoxLingo()
# Create the interface
interface = voxlingo.create_interface()
# For Hugging Face Spaces, we just need to expose the interface
app = interface

# If running locally, launch the interface
if __name__ == "__main__":
    app.launch()
