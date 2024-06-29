import streamlit as st
import streamlit.components.v1 as components
import os
from streamlit.components.v1 import html
# from jd_analyzer import analyze_jobs
# from resume_parser import parse_resumes
# from knowledge_graph import make_kg
# import plotly.express as px
# import pandas as pd
import tkinter as tk
from tkinter import filedialog
from pathlib import Path


root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)
selected_data_folder = ""
home_path = "" ##folder path
if os.path.exists("job_net1.html"):
    os.remove("job_net1.html")
if os.path.exists("path.txt"):
    os.remove("path.txt")
if os.path.exists("out.csv"):
    os.remove("out.csv")
if os.path.exists("skill_out.csv"):
    os.remove("skill_out.csv")
if os.path.exists("file.txt"):
    os.remove("file.txt")
if os.path.exists("pub_type.html"):
    os.remove("pub_type.html")
if os.path.exists("experience.html"):
    os.remove("experience.html")

st.set_page_config(page_title="CV Linker", layout="wide", initial_sidebar_state="collapsed")



def nav_page(page_name, timeout_secs=3):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)


st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)
with st.container():
    st.subheader("CV Linker Web App")
    st.title("Find Suitable Candidates for your Job Role Hassle Free")
    st.title('Select Data Folder')
    st.write('Please select a folder:')
    uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
    if uploaded_files is not None:
        for file in uploaded_files:
            file_path = Path(f'{home_path}/tmp/{file.name}')  # Save the uploaded file temporarily
            if not os.path.exists(f'{home_path}/tmp/'):
                os.makedirs(f'{home_path}/tmp/')
            # try:
            #     os.mknod(file_path)
            #     print(f"File '{file_path}' created successfully.")
            # except OSError as e:
            #     print(f"Error creating file: {e}")
            with open(file_path, 'w+') as f:
                f.write(file.getvalue().decode("utf-8"))
    clicked = st.button('Next Page')
    if clicked:
        # selected_data_folder = st.text_input('Selected folder:', filedialog.askdirectory(master=root))
        # f = open("path.txt", "w")
        # print(selected_data_folder)
        # f.write(selected_data_folder)
        # f.close()
        st.write("File uploaded!")
        nav_page("form")

