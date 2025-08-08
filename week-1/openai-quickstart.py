from openai import OpenAI
from dotenv import load_dotenv
import os

"""
This script demonstrates how to generate a response using the OpenAI API.
"""

# --------------------------------------------------------------
# Load environment variables
# --------------------------------------------------------------

load_dotenv()

# --------------------------------------------------------------
# Initialize OpenAI client
# --------------------------------------------------------------

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --------------------------------------------------------------
# Generate a response
# --------------------------------------------------------------

response = client.responses.create(
    model="gpt-4o", input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)
