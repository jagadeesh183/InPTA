import streamlit as st
from datetime import datetime, time
from script_animate_SepAng_ReadFile_SrcList import main, create_or_clear_directory, labeling
import os
import base64


with open("download.jpeg", "rb") as image_file:
    base64_icon = base64.b64encode(image_file.read()).decode()

st.set_page_config(
    page_title="Solar proximity prediction over the uGMRT antennas",
    page_icon=f"data:image/jpeg;base64,{base64_icon}",
    layout="wide"
)
theme = st.radio(
    "Choose Theme", 
    options=["Light Mode", "Dark Mode"], 
    horizontal=True
)

# Add a custom CSS for dark/light mode
if theme == "Dark Mode":
    st.markdown(
        """
        <style>
        body {
            background-color: #111;
            color: #EEE;
        }
        .stApp {
            background-color: #111;
            color: #EEE;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        body {
            background-color: #FFF;
            color: #000;
        }
        .stApp {
            background-color: #FFF;
            color: #000;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

st.write("This is an example of enabling only a dark/light mode toggle.")

###banner for devs#####################################################################################################
development_mode_css = """
    <style>
    .development-banner {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #ffcc00; /* Bright yellow for visibility */
        color: black;
        text-align: center;
        font-weight: bold;
        padding: 10px;
        z-index: 1000; /* Ensure it stays on top */
        border-bottom: 2px solid red;
    }
    .stApp {
        margin-top: 50px; /* Push content down to make space for the banner */
    }
    </style>
"""
is_under_development = True  # Toggle this to False to remove the banner

if is_under_development:
    st.markdown(development_mode_css, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="development-banner">
            🚧 This application is currently under development or maintenance. Some features might not work as expected. 🚧
        </div>
        """,
        unsafe_allow_html=True,
    )
##########################################################################################################


hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Hides the main Streamlit menu */
    footer {visibility: hidden;} /* Hides the default footer */
    header {visibility: hidden;} /* Hides the Streamlit header */
    #stSidebar {visibility: hidden;} /* Hides the sidebar */
    .stApp {
        padding-top: 0 !important;
        margin-top: -100px; /* Adjust margin to remove space */
    }
    html, body {
        margin: 0;
        padding: 0;
    }
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
            <img src="data:image/jpeg;base64,{encoded_header}" alt="Header Image" style="width: 200%; height: 200px;">
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    # Description below header
    st.markdown(
        """
        ### Solar Proximity Prediction over the uGMRT Antennas
        This tool evaluates the solar proximity of sources observed using the uGMRT. It identifies whether any sources — both target and phasing — are within a specified angular separation threshold from the Sun during the entire observation session.

        **Key Features:**
        1. Generates overlap times for sources that fall within the specified angular separation threshold.
        2. Creates detailed plots of Separation Angle vs. Time for all sources, which can be clicked to download.
        3. Provides a downloadable summary file (summary.txt) containing the results.

        **Notes:**
        - A typical threshold for solar proximity is around 9 degrees for InPTA regular observations.
        - To use this tool, either upload the source list file or paste the source list from your observation command file. The required columns are Source Name, RA, DEC, Epoch. If any additional columns are present, the tool can still function.  
        - An example line: J0613-0200&nbsp;&nbsp;&nbsp;&nbsp;06h13m43.90s&nbsp;&nbsp;&nbsp;&nbsp;-02d00'47.20"&nbsp;&nbsp;&nbsp;&nbsp;2000.0
        - Currently, this tool supports only sources observed from the uGMRT.
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <strong style="display: block; width: 100%; margin-top: 20px; border-top: 2px solid black; padding-top: 10px;"></strong>
        """,
        unsafe_allow_html=True,
    )



def display_form():
    custom_css = """
    <style>
    .source-header {
        display: grid;
        grid-template-columns: 125px 125px 125px 125px; /* Fixed-width columns */
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 0px; /* Removes extra space below headers */
        margin: 0;
        pading:0;
        padding-left: 1rem; /* Adds left padding for "Source" */
    }
    .source-header div {
        text-align: left; /* Align text to the left */
    }
    .stTextArea {
        margin-top: -10px !important; /* Removes extra space between header and textarea */
    }
    textarea {
        font-family: monospace !important; /* Ensures monospace font */
        white-space: pre !important; /* Retains all spaces and formatting */
        font-size: 14px; /* Ensures readable font size */
        line-height: 1.5; /* Makes it more legible */
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload a source list file (.txt)", type=["txt"], key="file_uploader"
    )
    st.markdown(
        """
        <div class="source-header">
            <div>Source</div>
            <div>RA</div>
            <div>Dec</div>
            <div>Epoch</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    srclist_data = ""
    if uploaded_file:
        srclist_data = uploaded_file.read().decode("utf-8")
        #st.text_area(
        #    label="",
        #    value=srclist_data,
        #    height=200,
        #    key="source_list_preview",
        #)
        #uploaded_file = None
    srclist_data = st.text_area(
            label="",
            value=srclist_data,
            placeholder="Paste the contents of the source list here...",
            height=200,
            key="source_list",
        )

    if srclist_data.strip():
        with open(SRCLIST_FILE, "w") as file:
            file.write(srclist_data)

    observation_date = st.date_input("Observation Date in IST (YYYY/DD/MM)")
    #observation_start_time = st.text_input("Observation Start Time in IST (HH:MM:SS)", placeholder="HH:MM:SS")
    st.markdown(
    """
    <style>
        .time-picker-label {
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: normal;
                margin-bottom: 8px;
                color: #333;
            }
        .time-picker-select {
            font-family: Arial, sans-serif;
            font-size: 14px;
            padding: 4px;
            border: 1px solid #d1d1d1;
            border-radius: 4px;
            background-color: #f9f9f9;
            width: 60px;
            text-align: center;
            appearance: none;
        }
        .time-picker-select:focus {
            outline: none;
            border-color: #85b7d9;
            box-shadow: 0 0 4px rgba(133, 183, 217, 0.5);
        }
    </style>
    """,
    unsafe_allow_html=True,
)
    st.markdown('<label class="time-picker-label">Select Observation Start Time in IST (HH:MM:SS):</label>', unsafe_allow_html=True)
    # Dropdowns for hour, minute, and second
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hour = st.selectbox(
            "Hour", options=list(range(24)), format_func=lambda x: f"{x:02d}", key="hour"
        )
    with col2:
        minute = st.selectbox(
            "Minute", options=list(range(60)), format_func=lambda x: f"{x:02d}", key="minute"
        )
    with col3:
        second = st.selectbox(
            "Second", options=list(range(60)), format_func=lambda x: f"{x:02d}", key="second"
        )
    observation_start_time = f"{hour:02d}:{minute:02d}:{second:02d}"
    st.write(f"Selected Observation Start Time: {observation_start_time}")
    start_time_ist = f"{observation_date} {observation_start_time}"
    observation_duration = st.number_input("Observation Duration (in hours)", min_value=0.0, step=0.1)
    threshold_angle = st.number_input("Threshold Separation Angle (degrees)", min_value=0.0, step=0.1)
    observatory_name = st.selectbox("Select Observatory", ["Please select your obs name", "uGMRT"])
    observatory_name = "GMRT" if observatory_name == "uGMRT" else None
    
    if st.button("Submit"):
        if srclist_data.strip() and observatory_name:
            with st.spinner("Processing may take some time please wait (2-3 mins)..."):
                filename_label = labeling(
                    observation_date.strftime('%Y-%m-%d'), observation_start_time
                )
                create_or_clear_directory(OUTPUT_DIR, filename_label)
                summary_file = os.path.join(OUTPUT_DIR, f"summary_{filename_label}.txt")
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
                    filename_label
                )
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
                    <div style="margin: 0px 0; display: flex; align-items: center;">
                        <a href="https://inpta.iitr.ac.in/" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">Home</a>
                        <a href="https://inpta.iitr.ac.in/research.html" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">Research</a>
                        <a href="https://inpta.iitr.ac.in/publications.html" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">Publications</a>
                        <a href="https://inpta.iitr.ac.in/resources.html" target="_blank" style="color: black; text-decoration: none; margin-right: 15px;">Resource</a>
                    </div>
                </div>
            </div>
            <div style="text-align: left; max-width: 50%; padding-left: 400px;">
                <p style="margin: 0; font-size: 12px; color: #000000; font-weight: bold;">
                    Indian Pulsar Timing Array
                </p>
                <p style="margin: 0; font-size: 12px; color: #000000;">
                    Indian Pulsar Timing Array Experiment (InPTA) is an Indo-Japanese collaboration pulsar timing experiment searching for low frequency nanoHz Gravitational Waves in operation since 2016.
                </p>
                <!-- Social Media Icons -->
    <div style="margin-top: 10px; display: flex; justify-content: flex-start; align-items: center; gap: 10px;">
        <a href="https://www.facebook.com/indianpta/" target="_blank" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook" style="width: 24px; height: 24px;">
        </a>
        <a href="https://x.com/InPTA_GW" target="_blank" style="text-decoration: none;">
            <img src="https://avatars.githubusercontent.com/u/50278?s=200&v=4" alt="Twitter" style="width: 24px; height: 24px;">
        </a>
        <a href="https://github.com/inpta" target="_blank" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub" style="width: 24px; height: 24px;">
        </a>
        <a href="https://www.researchgate.net/lab/Indian-Pulsar-Timing-Array-Bhal-CHANDRA-Joshi" target="_blank" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/ResearchGate_icon_SVG.svg" alt="ResearchGate" style="width: 24px; height: 24px;">
        </a>
        <a href="https://www.instagram.com/indian_pta/" target="_blank" style="text-decoration: none;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram" style="width: 24px; height: 24px;">
        </a>
                </div>
            </div>
        </div>
        <div style="text-align: center; font-size: 12px; margin-top: 10px;">
            <p style="margin: 0;">Developed by <strong>Jagadeesh S</strong> & <strong>Shaswata Chowdhury</strong></p>
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
