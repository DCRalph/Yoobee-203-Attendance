import os
import base64
from PIL import Image
from io import BytesIO
import psycopg2

from Common import Common


from Secrets import Secrets


db_connection = psycopg2.connect(Secrets.PG_URI)

# Define the cache directory
CACHE_DIR = "src/image_cache"

# Ensure the cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


def save_image_to_cache(image: Image.Image, image_id: str) -> str:
    # Define the path for the cached image
    image_path = os.path.join(CACHE_DIR, f"{image_id}.png")

    # Save the image to the cache
    image.save(image_path, format="PNG")

    # Convert the image to a base64 string
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    base64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return base64_str


def get_image_from_cache(image_id: str) -> Image.Image:
    # Define the path for the cached image
    image_path = os.path.join(CACHE_DIR, f"{image_id}.png")

    # Check if the image is in the cache
    if os.path.exists(image_path):
        return Image.open(image_path)

    # If not in cache, fetch from the database
    base64_str = fetch_from_database(image_id)

    # Convert the base64 string to a PIL image
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))

    # Save the image to the cache
    image.save(image_path, format="PNG")

    return image


def fetch_from_database(image_id: str) -> str:

    cur = db_connection.cursor()
    cur.execute('SELECT "pictures"."b64Img" FROM pictures WHERE id = %s', (image_id,))
    result = cur.fetchone()
    cur.close()


    if result:
        # print(result[0])
        return result[0]
    else:
        print("No image found")
        return None

if __name__ == "__main__":
    fetch_from_database("d30db3c5-fa82-43ee-bcf5-a5fd878c4447")