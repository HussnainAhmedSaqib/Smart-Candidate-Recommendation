import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import zlib
import zipfile
from streamlit.components.v1 import html
from streamlit_extras.switch_page_button import switch_page

# from zipfile import ZipFile
import os

res_path = '' ## set path where to store resumes (temp folder in your project directory)


# if os.path.exists("resumes.zip"):
#     os.remove("resumes.zip")

def compress(path, file_names):
    # print("File Paths:")
    # print(file_names)

    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED

    # create the zip file first parameter path/name, second mode
    zf = zipfile.ZipFile(os.path.join(path,"shortlisted_resumes.zip"), mode="w")
    try:
        for file_name in file_names:
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            # print(os.path.join(path, file_name))
            zf.write(os.path.join(path, file_name), file_name, compress_type=compression)


    except FileNotFoundError:
        print("An error occurred")
    finally:
        # Don't forget to close the file!
        # print("success")
        zf.close()


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


st.set_page_config(page_title="Shortlisted Candidates", layout="wide", initial_sidebar_state="collapsed")
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
# zip_path = ''
# try:
#     f = open("path.txt", "r")
#     print(f.read())
#     zip_path = f.read()
#     f.close()
# except:
#     pass
res_list = []
with st.container():
    st.subheader("CV Linker Web App")
    try:
        HtmlFile = open("job_net1.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.title("Knowledge Graph for Skill Matching")
        components.html(source_code, height=1000)
    except:
        st.caption("No reports found")

    try:
        HtmlFile = open("pub_type.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.title("Types of Publications")
        components.html(source_code, height=1000)
    except:
        st.caption("No reports found")

    try:
        skill_df = pd.read_csv('skill_out.csv')
        st.title("Candidates found")
        st.table(skill_df)
    except:
        pass
    try:
        HtmlFile = open("experience.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        st.title("Experience of Each Candidate")
        components.html(source_code, height=1000)
    except:
        st.caption("No reports found")
    # try:
    #     HtmlFile = open("publications.html", 'r', encoding='utf-8')
    #     source_code = HtmlFile.read()
    #     st.title("Publications of Each Candidate")
    #     components.html(source_code, height=1000)
    # except:
    #     st.caption("No reports found")
    try:
        df = pd.read_csv('out.csv')
        st.title("Final Candidate Rankings")
        st.table(df[['Name', 'total_score']].sort_values('total_score', ascending=False))
        res_list = df['Name'].values
    except:
        st.caption("No Table found")
    # f = open("path.txt", "r")
    # res_path = f.read()
    # f.close()
    # print(res_path)
    compress(res_path, res_list)

    with open(os.path.join(res_path, "shortlisted_resumes.zip"), "rb") as fp:
        btn = st.download_button(
            label="Download ZIP",
            data=fp,
            file_name="data.zip",
            mime="application/zip"
        )

    if btn:
        if os.path.exists(os.path.join(res_path, "shortlisted_resumes.zip")):
            os.remove(os.path.join(res_path, "shortlisted_resumes.zip"))

    # with ZipFile('resumes.zip', 'w') as zip:
    #     for file in zip_path:
    #         zip.write(file)
    # with open("resumes.zip", "rb") as fp:
    #     btn = st.download_button(
    #         label="Download",
    #         data=fp,
    #         file_name="resumes.zip",
    #         mime="application/zip"
    #     )
    if st.button("← Prev"):
        switch_page("form")
    if st.button("Home"):
        switch_page("main")
