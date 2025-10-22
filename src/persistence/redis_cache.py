import os
from dotenv import load_dotenv
load_dotenv()  # Add at top of files
uri = os.getenv('NEO4J_URI')
# etc.