import streamlit as st
from datetime import datetime
from script_animate_SepAng_ReadFile_SrcList import main, create_or_clear_directory
import os
import base64

# Set the favicon and layout
with open("download.jpeg", "rb") as image_file:
    base64_icon = base64.b64encode(image_file.read()).decode()

st.set_page_config(
    page_title="Observatory Data Input",
    page_icon=f"data:image/jpeg;base64,{base64_icon}",
    layout="wide"
)


# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_final")
SRCLIST_FILE = os.path.join(BASE_DIR, "Srclist.txt")
OBSRV_COORD_FILE = os.path.join(BASE_DIR, "ObservatoryCoord.txt")



def display_header():
    # Encode the logo image to Base64
    with open("InPTA_logo-removebg.png", "rb") as logo_file:
        encoded_logo = base64.b64encode(logo_file.read()).decode()

    # Encode the header image to Base64
    with open("gmrtarray_panorama1.jpg", "rb") as header_file:
        encoded_header = base64.b64encode(header_file.read()).decode()

    # HTML with Base64-encoded images
    header_html = f"""
    <div style="width: 100%; height: auto;">
        <!-- Logo on top left, clickable to homepage -->
        <a href="https://inpta.iitr.ac.in/" target="_blank">
            <img src="data:image/png;base64,{encoded_logo}" alt="InPTA Logo" style="width: 100px; height: auto; position: absolute; top: 20px; left: 20px; z-index: 100;">
        </a>
        <!-- Header Image with full width -->
        <div style="margin-top: 80px;"> <!-- Adjusting this margin to give space below the logo -->
            <img src="data:image/jpeg;base64,{encoded_header}" alt="Header Image" style="width: 100%; height: auto;">
        </div>
    </div>
    """
    # Render the HTML in Streamlit
    st.markdown(header_html, unsafe_allow_html=True)


def display_form():
    st.title("Observatory Data Input")

    # Text area for pasting Srclist data
    srclist_data = st.text_area("Paste Srclist Data Here", placeholder="Paste the contents of Srclist.txt")

    # Save the pasted data to a file
    if srclist_data.strip():  # Only proceed if the user has entered text
        with open(SRCLIST_FILE, "w") as file:
            file.write(srclist_data)

    # Observation date input
    observation_date = st.date_input("Observation Date (DD-MM-YYYY)")

    # Observation start time input
    observation_start_time = st.text_input("Observation Start Time (HH:MM:SS)", placeholder="HH:MM:SS")

    # Combine date and time into a single string
    start_time_ist = f"{observation_date} {observation_start_time}"

    # Observation duration input
    observation_duration = st.number_input("Observation Duration (in hours)", min_value=0.0, step=0.1)

    # Threshold separation angle input
    threshold_angle = st.number_input("Threshold Separation Angle (degrees)", min_value=0.0, step=0.1)

    # Observatory name dropdown
    observatory_name = st.selectbox("Select Observatory", ["GMRT", "VLA"])

    # Create or clear the summary file
    summary_file = create_or_clear_directory(OUTPUT_DIR)
    with open(summary_file, "a") as file:
        file.write(f"Observatory Name: {observatory_name}\n")
        file.write(f"Start Time: {start_time_ist}\n")
        file.write(f"Observation Duration: {observation_duration}\n")

    # Submit button
    if st.button("Submit"):
        if srclist_data.strip() and observatory_name:
            with st.spinner("Processing..."):
                # Call the backend code to generate plots and save outputs
                main(
                    OBSRV_COORD_FILE,
                    OUTPUT_DIR,
                    summary_file,
                    SRCLIST_FILE,
                    start_time_ist,
                    observation_duration,
                    threshold_angle,
                    observatory_name,
                )
            st.success("Processing complete. Please find the output below.")

            # Display the summary file
            with open(summary_file, "r") as file:
                summary_contents = file.read()
            st.subheader("Summary File Contents:")
            st.text(summary_contents)

            # Save the output folder path to session state
            st.session_state["output_folder"] = OUTPUT_DIR


def display_pdfs():
    # Display output PDFs
    if "output_folder" in st.session_state:
        output_folder = st.session_state["output_folder"]
        st.subheader("View Generated PDFs:")
        for filename in os.listdir(output_folder):
            if filename.endswith(".pdf"):
                file_path = os.path.join(output_folder, filename)
                with open(file_path, "rb") as pdf_file:
                    pdf_base64 = base64.b64encode(pdf_file.read()).decode("utf-8")
                file_url = f"data:application/pdf;base64,{pdf_base64}"
                st.markdown(f'<a href="{file_url}" target="_blank">{filename}</a>', unsafe_allow_html=True)


def display_footer():
    # Encode the small image (footer logo)
    with open("download.jpeg", "rb") as footer_file:
        encoded_footer = base64.b64encode(footer_file.read()).decode()

    footer_html = f"""
    <div style="background-color: #f0f0f0; color: black; padding: 20px; font-family: Arial, sans-serif; bottom: 0; left: 0; width: 100%; z-index: 1000;">
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; max-width: 100%;">
            <!-- Left Section -->
            <div style="display: flex; align-items: center;">
                <img src="data:image/jpeg;base64,{encoded_footer}" alt="Footer Logo" style="width: 50px; height: auto; margin-right: 15px;">
                <div>
                    <h1 style="color: #00008B; margin: 0;">Indian Pulsar Timing Array</h1>
                    <div style="margin: 10px 0; display: flex; align-items: center;">
                        <a href="https://inpta.iitr.ac.in/" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">Home</a>
                        <a href="https://www.instagram.com/indian_pta/" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">Instagram</a>
                        <a href="https://www.researchgate.net/lab/Indian-Pulsar-Timing-Array-Bhal-CHANDRA-Joshi" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">ResearchGate</a>
                        <a href="https://github.com/inpta" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">GitHub</a>
                        <a href="https://x.com/i/flow/login?redirect_after_login=%2FInPTA_GW" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">X</a>
                        <a href="https://www.facebook.com/indianpta/" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">Facebook</a>
                    </div>
                </div>
            </div>
        </div>
        <!-- Credits Section -->
        <div style="text-align: center; font-size: 12px; margin-top: 10px;">
            <p style="margin: 0;">Developed by <strong>S Jagadeesh</strong> & <strong>Shaswata Chowdhury</strong></p>
            <a href="mailto:shaswataphyres@gmail.com" style="color: blue; text-decoration: none; font-size: 12px;">Contact Us</a>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


# Main App
if __name__ == "__main__":
    display_header()
    display_form()
    display_pdfs()
    display_footer()
