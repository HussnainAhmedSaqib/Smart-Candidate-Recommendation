import streamlit as st
import streamlit.components.v1 as components
import os
from streamlit.components.v1 import html
from jd_analyzer import analyze_jobs
from resume_parser import parse_resumes
from knowledge_graph import make_kg
import plotly.express as px
import pandas as pd
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)
selected_data_folder = ""

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
dir_list = []
with st.container():
    st.subheader("CV Linker Web App")
    st.title("Find Suitable Candidates for your Job Role Hassle Free")
    choice = st.radio(
        "Are you hiring for the Industry or the Academia?",
        ["Academia", "Industry"],
    )
    st.title('Folder Picker')
    st.write('Please select a folder:')
    clicked = st.button('Select directory')
    if clicked:
        selected_data_folder = st.text_input('Selected folder:', filedialog.askdirectory(master=root))
    f = open("path.txt", "w")
    f.write(selected_data_folder)
    f.close()

    st.title('Fill in the form')

    with st.form(key='my_form'):

        text_input = st.text_area(label="Please Enter Job Description:", placeholder="Type/paste job description here")
        req_experience = st.number_input('Enter the number of years of experience required:', value=0, step=1)
        req_publications = st.number_input('Enter the number of publications required:', value=0, step=1)
        experience_multiplier = st.number_input('Assign weight to Experiences:', value=1.0, step=0.5)
        publications_multiplier = st.number_input('Assign weight to Publications:', value=1.0, step=0.5)

        # data_path = '/home/hussnain/PycharmProjects/thesis/data'

        # for directory in os.listdir(data_path):
        #     dir_list.append(directory)



        if st.form_submit_button('Submit'):
            f = open("path.txt", "r")
            res_path = f.read()
            f.close()

            print("hello")
            print(res_path)


            if text_input != "":
                # print(text_input, req_experience, req_publications, selected_data_folder)
                # status = False
                # while not status:
                results = analyze_jobs([text_input])
                data_graph = {
                    'JOBID': ['asdk'],
                    'skills': [results[0]],
                    'experience_skills': [results[1]],
                    'experience_year': [results[2]],
                    'diploma': [results[3]],
                    'diploma_major': [results[4]],
                }
                for i in range(len(data_graph['experience_year'])):
                    data_graph['experience_year'][i] = data_graph['experience_year'][i][0]


                # df = parse_resumes("/".join([data_path, selected_data_folder]))
                print(res_path)
                df = parse_resumes(res_path)
                data_graph_resume = {
                    'document': df['Name'],
                    'skills': df['Skills']
                }
                ######## For Skills #######
                resumeslist, skillslist = make_kg(data_graph, data_graph_resume, len(df))
                if choice.lower() == 'industry':
                    skill_df = pd.DataFrame.from_records(skillslist, columns=['Skill', 'Count'])
                    skill_df.to_csv('skill_out.csv', index=False)
                # print(len(df))
                ######## For Experience #######
                # print(df.sort_values('Experience', ascending=False))
                exp_fig = px.bar(df.sort_values('Experience', ascending=False), x='Name', y='Experience')
                exp_fig.write_html("experience.html")
                exp_fig.update_xaxes(categoryorder="total ascending")
                ######## For Publications #######
                num_of_pubs = []
                for i in range(len(df)):
                    num_of_pubs.append(len(df['Publications'].iloc[i]))
                # print(df['Publications'].iloc[0])
                df["publication_count"] = num_of_pubs

                pub_score = [x * experience_multiplier for x in num_of_pubs]
                exp_score = [x * publications_multiplier for x in df['Experience'].values]
                total_score = [x + y for x, y in zip(pub_score, exp_score)]
                df['total_score'] = total_score
                df.to_csv('out.csv', index=False)

                pub_fig = px.bar(df.sort_values('publication_count', ascending=False), x='Name', y='publication_count')
                pub_fig.write_html("publications.html")
                pub_fig.update_xaxes(categoryorder="total ascending")
                # print(df.sort_values('publication_count', ascending=False))
                # status = True
                nav_page("report")
            else:
                st.error('Job description in Empty', icon="🚨")

        # HtmlFile = open("job_net1.html", 'r', encoding='utf-8')
        # source_code = HtmlFile.read()
        # # print(source_code)
        # components.html(source_code, height=1500)
        # st.success('This is a success message!', icon="✅")
