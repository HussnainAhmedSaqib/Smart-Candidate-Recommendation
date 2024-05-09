import os
import pandas as pd
import spacy
from experience_helper.experience_extractor import get_experience
import re
import pyarrow as pa
import pyarrow.parquet as pq
import json
from openai import OpenAI


def publication_type(input_str):
    journal_substring = r'\b(journal|transactions|letters)\b'
    conference_substring = r'\b(conference|symposium|workshop)'

    conference_count = len(re.findall(conference_substring, input_str.lower()))
    journal_count = len(re.findall(journal_substring, input_str.lower()))

    return conference_count, journal_count


def load_db():
    if os.path.exists("resumes_db.parquet"):
        table = pq.read_table("resumes_db.parquet")
        df = table.to_pandas()
        return df
    else:
        return pd.DataFrame()


def add_to_db(new_df):
    combined_df = pd.DataFrame()
    if os.path.exists("resumes_db.parquet"):
        table = pq.read_table("resumes_db.parquet")
        df = table.to_pandas()
        combined_df = pd.concat([df, new_df], axis=0)
        combined_df.reset_index(drop=True, inplace=True)
    else:
        combined_df = new_df

    combined_pq = pa.Table.from_pandas(combined_df)
    pq.write_table(combined_pq, 'resumes_db.parquet')
    # combined_df.to_csv("resumes_db.csv", index=False)
    return combined_df


def parse_resumes(resumes_path, model_path):
    print(resumes_path)
    files = os.listdir(resumes_path)

    candidate_list = []
    old_df = load_db()
    if len(old_df) > 0:
        old_files = set(old_df['Name'].values)
        temp_files = set(files)
        files = temp_files.difference(old_files)

    if model_path != "":
        print(model_path)
        nlp = spacy.load(model_path)
        for file in files:
            print(f'{resumes_path}/{file}')

            f = open(f'{resumes_path}/{file}', "r")
            mystr = f.read()
            # print(f'{resumes_path}/{file}')
            # print(mystr)

            doc = nlp(mystr)
            # spacy.displacy.render(doc, style="ent")
            # print(get_experience(doc))
            skills, pub, maj, degr = [], [], [], []
            for word in doc.ents:
                # print(word.label_, doc.text[word.start_char:word.end_char])
                if word.label_ == "skills":
                    skills.append(doc.text[word.start_char:word.end_char])
                if word.label_ == "degree":
                    degr.append(doc.text[word.start_char:word.end_char])
                if word.label_ == "majors":
                    maj.append(doc.text[word.start_char:word.end_char])
                if word.label_ == "publications":
                    pub.append(doc.text[word.start_char:word.end_char])
            conference_count, journal_count = publication_type(doc.text)
            unk_count = len(pub) - (conference_count + journal_count)
            candidate_list.append(
                [file, skills, degr, maj, pub, get_experience(doc), conference_count, journal_count, unk_count])
    else:
        f = open("key.txt", "r")
        api_key = f.read()
        f.close()
        os.environ["OPENAI_API_KEY"] = api_key.split('\n')[0]
        client = OpenAI()
        instruction = '''I want to perform Named Entity Recognition (NER) on resumes. I want to extract degrees' title, the major of their degree, their total work experience, their technical skills, and the title of their publications if they have any.  I need to separate my degree and the subject in which i am doing my degree in as well
        Extract this information in a JSON object. \n I have the following labels: \n degree: whether the degree is a bachelors, masters, PhD etc \n majors: in which subject the degree is like computer science, data science, electrical engineering \n skills: what different technical and soft skills the candidate has \n
        experience: take all the jobs the candidate has held and calculate total work experience in years \n
        publications: whether the candidate has had any papers or research published, just the titles of their research. \n
        Don't break down skills into multiple categories, only keep 1 category as mentioned in this instruction. For the degree i just need the type of degree, and major of degree.
        Do not include any explanations, only provide a  RFC8259 compliant JSON response  following this format without deviation.
        [{'degrees': 
        {'degree': 'whether the degree is a bachelors, masters, PhD etc', 
        'major': 'in which subject the degree is like computer science, data science, electrical engineering'}, 
        'experience': 'take all the jobs the candidate has held and calculate total work experience in years eg 11.0, if they are a fresher, or have no job experience write 0', 
        'skills': what different technical and soft skills the candidate has all grouped into a single list, 
        'publications': whether the candidate has had any research academic papers published, just a list of the titles of their academic research papers. if they don't have any papers, it can be an empty list. }
        ] \n
        Follow this format strictly. \n
        Do it for the following resume: \n \n \n'''

        for file in files:
            print(f'{resumes_path}/{file}')
            f = open(f'{resumes_path}/{file}', "r")
            mystr = f.read()
            input_str = instruction + mystr
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system",
                     "content": "you are an information extraction system designed to extract information from resumes and return json object."},
                    {"role": "user", "content": input_str}
                ]
            )

            skills, pub, maj, degr = [], [], [], []
            output_dict = json.loads(response.choices[0].message.content)
            print(output_dict)
            skills = output_dict['skills']
            pub = output_dict['publications']
            try:
                for degree in output_dict['degrees']:
                    try:
                        degr.append(degree['type'])
                    except:
                        degr.append(degree['degree'])
                        continue
                    maj.append(degree['major'])
            except:
                degr.append(output_dict['degrees']['degree'])
                maj.append(output_dict['degrees']['major'])
                continue

            conference_count, journal_count = publication_type(mystr)
            if len(pub) > 0:
                unk_count = len(pub) - (conference_count + journal_count)
            else:
                unk_count = 0
                conference_count = 0
                journal_count = 0

            candidate_list.append(
                [file, skills, degr, maj, pub, float(output_dict['experience'].split()[0]), conference_count,
                 journal_count, unk_count])

    df = pd.DataFrame(candidate_list,
                      columns=["Name", "Skills", "Degrees", "Majors", "Publications", "Experience", 'Conference',
                               'Journal', 'Unknown'])
    for i in range(len(df)):
        df['Skills'].iloc[i] = list(dict.fromkeys(df['Skills'].iloc[i]))
    new_df = add_to_db(df)
    # print(df)
    # print(len(new_df))
    # return df
    return new_df
