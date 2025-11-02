from backend.initial_setup import base

# change this variable to track if user has initialized the application before (?)
initialized = False

if not initialized:
    base.setup()