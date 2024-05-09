import streamlit as st
import streamlit.components.v1 as components
import os
from streamlit.components.v1 import html
from jd_analyzer import analyze_jobs
from resume_parser import parse_resumes
from knowledge_graph import make_kg
import plotly.express as px
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

# if os.path.exists("job_net1.html"):
#     os.remove("job_net1.html")
# if os.path.exists("path.txt"):
#     os.remove("path.txt")
# if os.path.exists("out.csv"):
#     os.remove("out.csv")
# if os.path.exists("skill_out.csv"):
#     os.remove("skill_out.csv")
# if os.path.exists("file.txt"):
#     os.remove("file.txt")

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
    choice = st.radio(
        "Are you hiring for the Industry or the Academia?",
        ["Industry", "Academia"],
    )
    st.title("Select a Model")
    model_choice = st.radio(
        "Which Model Would You Like to Use",
        ["XLNet", "Roberta", "ChatGPT"],
    )
    st.title('Fill in the form')
    with st.form(key='my_form'):

        text_input = st.text_area(label="Please Enter Job Description:", placeholder="Type/paste job description here")
        req_experience = st.number_input('Enter the number of years of experience required:', value=0.0, step=1.0)
        req_publications = st.number_input('Enter the number of publications required:', value=0.0, step=1.0)
        skills_multiplier = st.number_input('Assign weight to Skills:', value=1.0, step=0.5)
        experience_multiplier = st.number_input('Assign weight to Experiences:', value=1.0, step=0.5)
        publications_multiplier = st.number_input('Assign weight to Publications:', value=1.0, step=0.5)

        if st.form_submit_button('Submit'):
            f = open("path.txt", "r")
            res_path = f.read()
            f.close()
            if os.path.exists(os.path.join(res_path, "shortlisted_resumes.zip")):
                os.remove(os.path.join(res_path, "shortlisted_resumes.zip"))

            # print("hello")
            # print(res_path)

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
                    try:
                        data_graph['experience_year'][i] = data_graph['experience_year'][i][0]
                    except:
                        print("Empty list")
                        break

                # df = parse_resumes("/".join([data_path, selected_data_folder]))
                # print(res_path)
                if model_choice.lower() == 'xlnet':
                    model_path = "/home/hussnain/PycharmProjects/thesis/models/xlnet-ner-experience-full-20230405T215230Z-001/xlnet-ner-experience-full/xlnet_model/en_pipeline-0.0.0/en_pipeline/en_pipeline-0.0.0"
                elif model_choice.lower() == 'roberta':
                    model_path = "/home/hussnain/PycharmProjects/thesis/models/roberta-ner-experience-full-20240302T133501Z-001/roberta-ner-experience-full/roberta_model/en_pipeline-0.0.0/en_pipeline/en_pipeline-0.0.0"
                else:
                    model_path = ""
                df = parse_resumes(res_path, model_path)

                num_of_pubs = []
                for i in range(len(df)):
                    num_of_pubs.append(len(df['Publications'].iloc[i]))
                df["publication_count"] = num_of_pubs
                ##### Initial Filtering ######
                # print(req_publications, req_experience)
                # print(len(df))
                # df = df[(df["publication_count"] >= req_publications) & (df["Experience"] >= req_experience)]
                # df = df.reset_index()
                # print(len(df))


                if choice.lower() == 'industry':
                    link = 'skills'
                    data_graph_resume = {
                        'document': df['Name'],
                        'link': df['Skills']
                    }
                    ######## For Skills #######
                    resumeslist, skillslist = make_kg(data_graph, data_graph_resume, len(df), link)

                    skill_df = pd.DataFrame.from_records(skillslist, columns=['Skill', 'Count'])
                    # skill_df.to_csv('skill_out.csv', index=False)
                    resume_df = pd.DataFrame.from_records(resumeslist, columns=['Name', 'Skills_count'])
                    df2 = pd.merge(df, resume_df, on=['Name'])
                    skills_found = []
                    for i in range(len(df2)):
                        skills_found.append(
                            [value for value in list(df2['Skills'].iloc[i]) if value in list(skill_df['Skill'])])
                    print(skills_found)
                    df2['Skills_found'] = skills_found
                    num_of_skills_found = []
                    for i in range(len(df2)):
                        num_of_skills_found.append(len(df2['Skills_found'].iloc[i]))
                    df2['Skills_found_count'] = num_of_skills_found
                    df2[['Name', 'Skills_found', 'Skills_found_count']][df2['Skills_found_count'] > 0].to_csv(
                        'skill_out.csv', index=False)
                else:
                    link = 'diploma_major'
                    data_graph_resume = {
                        'document': df['Name'],
                        'link': df['Majors']
                    }
                    ######## For Skills #######
                    resumeslist, majorslist = make_kg(data_graph, data_graph_resume, len(df), link)
                    resume_df = pd.DataFrame.from_records(resumeslist, columns=['Name', 'Majors_count'])
                    df2 = pd.merge(df, resume_df, on=['Name'])
                    num_of_skills_found = []
                    for i in range(len(df2)):
                        num_of_skills_found.append(0)
                    major_df = pd.DataFrame.from_records(majorslist, columns=['Majors', 'Count'])
                    majors_found = []
                    # df2 = df
                    for i in range(len(df2)):
                        majors_found.append(
                            [value for value in list(df2['Majors'].iloc[i]) if value in list(major_df['Majors'])])
                    print(majors_found)
                    df2['Majors_found'] = majors_found
                    num_of_majors_found = []
                    for i in range(len(df2)):
                        num_of_majors_found.append(len(df2['Majors_found'].iloc[i]))
                    df2['Majors_found_count'] = num_of_majors_found
                    df2[['Name', 'Majors_found', 'Majors_found_count']][df2['Majors_found_count'] > 0].to_csv(
                        'skill_out.csv', index=False)

                    # print(df)

                # print(resumeslist,skillslist)
                # print(len(df))
                ######## For Experience #######
                # print(df.sort_values('Experience', ascending=False))
                df_melted = pd.melt(df2[["Name", "Conference", "Journal", "Unknown"]],
                                    id_vars=['Name'], var_name='Publication_Type', value_name='Count')
                # print(df_melted)
                pub_type_fig = px.bar(df_melted, x='Name', y='Count', color='Publication_Type', barmode='group',
                                      color_discrete_sequence=["red", "green", "blue"])
                pub_type_fig.write_html("pub_type.html")

                exp_fig = px.bar(df2.sort_values('Experience', ascending=False), x='Name', y='Experience')
                exp_fig.write_html("experience.html")
                exp_fig.update_xaxes(categoryorder="total ascending")
                ######## For Publications #######
                # num_of_pubs = []
                # for i in range(len(df2)):
                #     num_of_pubs.append(len(df2['Publications'].iloc[i]))
                # # print(df['Publications'].iloc[0])
                # df2["publication_count"] = num_of_pubs


                skills_score = [x * skills_multiplier for x in num_of_skills_found]
                pub_score = [x * experience_multiplier for x in num_of_pubs]
                exp_score = [x * publications_multiplier for x in df2['Experience'].values]
                total_score = [x + y + z for x, y, z in zip(pub_score, exp_score, skills_score)]
                df2['total_score'] = total_score
                df2 = df2[(df2["publication_count"] >= req_publications) & (df2["Experience"] >= req_experience)]
                df2 = df2.reset_index()
                df2.to_csv('out.csv', index=False)

                # pub_fig = px.bar(df2.sort_values('publication_count', ascending=False), x='Name', y='publication_count')
                # pub_fig.write_html("publications.html")`
                # pub_fig.update_xaxes(categoryorder="total ascending")
                # print(df.sort_values('publication_count', ascending=False))
                # status = True
                nav_page("newreport")
            else:
                st.error('Job description in Empty', icon="🚨")
    if st.button("← Prev"):
        switch_page("testapp")
        # HtmlFile = open("job_net1.html", 'r', encoding='utf-8')
        # source_code = HtmlFile.read()
        # # print(source_code)
        # components.html(source_code, height=1500)
        # st.success('This is a success message!', icon="✅")
