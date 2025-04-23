import requests
import os

def download_image(image_url, output_folder, title):
    """Download and save the image locally."""
    if not image_url:
        return None

    os.makedirs(output_folder, exist_ok=True)

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            sanitized_title = "".join([c for c in title if c not in r'\/:*?"<>|']).strip()
            image_filename = os.path.join(output_folder, f"{sanitized_title}.jpg")
            with open(image_filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return os.path.abspath(image_filename)
        else:
            print(f"❌ Image upload failed. Response code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error loading image: {e}")
    return None
