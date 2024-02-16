import streamlit as st
from PIL import Image
import os
import  cv2
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
from io import BytesIO
import base64
import tempfile



def recognize_faces(image_np):
    # Load the pre-trained face detection model
    face_locations = face_recognition.face_locations(image_np)
    # Draw rectangles around the faces
    for top, right, bottom, left in face_locations:
        cv2.rectangle(image_np, (left, top), (right, bottom), (0, 255, 0), 2)
    return image_np





# Function to display images and provide download option
def display_images(images):
    for image in images:
        st.image(image, caption='Recognized Faces', use_column_width=True)
        # Provide a download link for the image
        st.markdown(get_image_download_link(image), unsafe_allow_html=True)

# Function to generate a download link for an image
def get_image_download_link(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/jpg;base64,{img_str}" download="recognized_face.jpg">Download image</a>'
    return href

# Path to store the downloaded JSON file
json_file_path = "imapp.json"

# Download the JSON file if it does not exist
if not os.path.exists(json_file_path):
    url = "https://github.com/Sagarnr1997/Image_app/blob/main/imapp.json?raw=true"
    response = requests.get(url)
    with open(json_file_path, 'wb') as f:
        f.write(response.content)

# Authenticate with Google Drive API using the downloaded JSON file
def authenticate():
    creds = service_account.Credentials.from_service_account_file(json_file_path, scopes=['https://www.googleapis.com/auth/drive'])
    return creds

# List image files from Google Drive
def list_image_files():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(
        q="mimeType='image/jpeg' or mimeType='image/png'",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    image_files = []
    if not items:
        print('No image files found.')
    else:
        for item in items:
            image_files.append(item['id'])
    return image_files

# Get image data from Google Drive
def get_image_from_drive(file_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    request = service.files().get_media(fileId=file_id)
    image_data = request.execute()
    image = Image.open(BytesIO(image_data))
    return image

# Main function
# Main function
def main():
    st.title("Face Recognition App")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image_np = np.array(image)  # Convert the image to a numpy array
        modified_image = recognize_faces(image_np)  # Perform facial recognition and get the modified image
        st.image(modified_image, caption='Uploaded Image with Recognized Faces', use_column_width=True)
    else:
        st.write("Please upload an image to recognize faces.")

    # Display recognized images from Google Drive
    if st.button('Display Recognized Images'):
        image_files = list_image_files()
        images = []
        for file_id in image_files:
            image = get_image_from_drive(file_id)
            faces_detected = recognize_faces(np.array(image))
            if len(faces_detected) > 0:
                images.append(image)
        if images:
            display_images(images)
        else:
            st.write("No faces detected in any of the images.")

if __name__ == "__main__":
    main()
