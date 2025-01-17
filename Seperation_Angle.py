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

hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Hides the main Streamlit menu */
    footer {visibility: hidden;} /* Hides the default footer */
    header {visibility: hidden;} /* Hides the Streamlit header */
    #stSidebar {visibility: hidden;} /* Hides the sidebar */
    .stApp {padding-top: 0 !important;}
    .css-1u3zpt6 {visibility: hidden;} /* Hides user settings menu */
    .viewerBadge_container__1QSob {display: none !important;} /* Hides "Hosted with Streamlit" badge */
    footer {visibility: hidden !important;} /* Hides "Created by <username>" text */
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_final")
SRCLIST_FILE = os.path.join(BASE_DIR, "Srclist.txt")
OBSRV_COORD_FILE = os.path.join(BASE_DIR, "ObservatoryCoord.txt")

# Initialize session state
if "output_folder" not in st.session_state:
    st.session_state["output_folder"] = None
if "generated_files" not in st.session_state:
    st.session_state["generated_files"] = []

def display_header():
    with open("InPTA_logo-removebg.png", "rb") as logo_file:
        encoded_logo = base64.b64encode(logo_file.read()).decode()

    with open("gmrtarray_panorama1.jpg", "rb") as header_file:
        encoded_header = base64.b64encode(header_file.read()).decode()

    header_html = f"""
    <div style="width: 100%; height: auto;">
        <a href="https://inpta.iitr.ac.in/" target="_blank">
            <img src="data:image/png;base64,{encoded_logo}" alt="InPTA Logo" style="width: 100px; height: auto; position: absolute; top: 20px; left: 20px; z-index: 100;">
        </a>
        <div style="margin-top: 80px;">
            <img src="data:image/jpeg;base64,{encoded_header}" alt="Header Image" style="width: 100%; height: auto;">
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def display_form():
    st.title("Observatory Data Input")

    # Add custom CSS for monospace font in text area
    custom_text_area_style = """
    <style>
    textarea {
        font-family: monospace !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    </style>
    """
    st.markdown("**Source List Format:**")
    st.markdown("""
    | **Source** | **RA**          | **Date**          | **Epoch** | **Obs Duration** |
    |------------|-----------------|------------------|-----------|------------------|
    """)

    # Text area for source list input
    # Text area for source list input
    srclist_data = st.text_area(
    label=" ",  # Use a space to suppress the label but avoid extra newline
    placeholder="Paste the contents of the source list here...",
    height=300  # Optional: Adjust height as needed
)



# Updated text area
    # srclist_data = st.text_area(
    #     "Paste Source List",
    #     placeholder=f"{source_list_headings}Paste the contents of Source List here...",
    #     height=300  # Optional: Adjust height as needed
    # )


    if srclist_data.strip():
        with open(SRCLIST_FILE, "w") as file:
            file.write(srclist_data)

    observation_date = st.date_input("Observation Date (YYYY/DD/MM)")
    observation_start_time = st.text_input("Observation Start Time in IST (HH:MM:SS)", placeholder="HH:MM:SS")
    start_time_ist = f"{observation_date} {observation_start_time}"
    observation_duration = st.number_input("Observation Duration (in hours)", min_value=0.0, step=0.1)
    threshold_angle = st.number_input("Threshold Separation Angle (degrees)", min_value=0.0, step=0.1)
    observatory_name = st.selectbox("Select Observatory", ["Please select your obs name", "GMRT"])
    
    

    if st.button("Submit"):
        if srclist_data.strip() and observatory_name:
            with st.spinner("Processing..."):
                create_or_clear_directory(OUTPUT_DIR)
                summary_file = os.path.join(OUTPUT_DIR, "summary.txt")
                with open(summary_file, 'a') as file:
                    file.write(f"Observatory Name: {observatory_name} \n")
                    file.write(f"Start Time: {start_time_ist} \n")
                    file.write(f"Observation Duration: {observation_duration} \n")
    
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
    
                # Update session state for summary contents and generated files
                with open(summary_file, "r") as file:
                    st.session_state["summary_contents"] = file.read()
    
                st.session_state["output_folder"] = OUTPUT_DIR
                st.session_state["generated_files"] = [
                    f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))
                ]
    
            st.success("Processing complete. Files are ready for download below.")
    
    if "summary_contents" in st.session_state:
        st.subheader("Summary File Contents:")
        st.code(st.session_state["summary_contents"], language="text")
    #else:
        #st.warning("No summary file available. Please submit the form.")



def display_pdfs():
    if st.session_state["output_folder"] and st.session_state["generated_files"]:
        st.subheader("View and Download Generated Files:")
        for filename in st.session_state["generated_files"]:
            file_path = os.path.join(st.session_state["output_folder"], filename)
            with open(file_path, "rb") as file:
                file_data = file.read()

            st.download_button(
                label=f"Download {filename}",
                data=file_data,
                file_name=filename,
                mime="application/octet-stream",
            )
   # else:
        #st.info("No files available for download. Please submit the form to generate files.")

def display_footer():
    with open("download.jpeg", "rb") as footer_file:
        encoded_footer = base64.b64encode(footer_file.read()).decode()

    footer_html = f"""
    <div style="background-color: #f0f0f0; color: black; padding: 20px; font-family: Arial, sans-serif; bottom: 0; left: 0; width: 100%; z-index: 1000;">
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%; max-width: 100%;">
            <div style="display: flex; align-items: center;">
                <img src="data:image/jpeg;base64,{encoded_footer}" alt="Footer Logo" style="width: 70px; height: 70; margin-right: 15px;">
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
