import random
import string
import spacy
from spacy.tokens import DocBin, Doc
from spacy.training.example import Example
from models.roberta_re.roberta_re.roberta_model.rel_component.rel_pipe import make_relation_extractor, score_relations
from models.roberta_re.roberta_re.roberta_model.rel_component.rel_model import create_relation_model, \
    create_classification_layer, create_instances, create_tensors

# jobid_list=[]
skill_list = []
experience_year_list = []


def post_process_skills(skill_list_unprocessed):
    new_skill_list = []
    for item in skill_list_unprocessed:
        new_skill_list.extend(item.split("\\"))
    return new_skill_list


def analyze(text):
    nlp = spacy.load(
        "/home/hussnain/PycharmProjects/thesis/models/job_description_ner/job_description/NER/xlnet_ner/en_pipeline-0.0.0/en_pipeline/en_pipeline-0.0.0")
    nlp2 = spacy.load(
        "/home/hussnain/PycharmProjects/thesis/models/roberta_re/roberta_re/roberta_model/rel_component/training/model-best")
    nlp2.add_pipe('sentencizer')
    experience_year = []
    experience_skills = []
    diploma = []
    diploma_major = []
    # for doc in nlp.pipe(text, disable=["tagger"]):
    #    print(f"spans: {[(e.start, e.text, e.label_) for e in doc.ents]}")
    for doc in nlp.pipe(text, disable=["tagger"]):
        skills = [e.text for e in doc.ents if e.label_ == 'SKILLS']
        skills = post_process_skills(skills)
        print(skills)
    for name, proc in nlp2.pipeline:
        doc = proc(doc)
    for value, rel_dict in doc._.rel.items():
        for e in doc.ents:
            for b in doc.ents:
                if e.start == value[0] and b.start == value[1]:
                    if rel_dict['EXPERIENCE_IN'] >= 0.9:
                        experience_skills.append(b.text)
                        experience_year.append(e.text)
                    if rel_dict['DEGREE_IN'] >= 0.9:
                        diploma_major.append(b.text)
                        diploma.append(e.text)
    return skills, experience_skills, experience_year, diploma, diploma_major


def analyze_jobs(jd_list):
    for i, row in enumerate(jd_list):
        try:
            print(i)
            # print(row)
            # skill, experience_skills, experience_year, diploma, diploma_major=analyze([row])
            # jobid_list.append(item['jobID'][i])
            # skill_list.append(skill)
            # experience_year_list.append(experience_year)
            return analyze([row])
        except:
            continue
