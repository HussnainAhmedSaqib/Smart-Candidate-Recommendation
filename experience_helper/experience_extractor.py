import re
from datetime import datetime
from dateutil import relativedelta
from dateutil import parser

def get_total_experience(experience_list):
    '''
    Wrapper function to extract total months of experience from a resume
    :param experience_list: list of experience text extracted
    :return: total months of experience
    '''
    exp_ = []
    for line in experience_list:
        experience = re.search(
            r'(?P<fmonth>\w+.\d+)\s*(\D|to)\s*(?P<smonth>\w+.\d+|present|current|now)',
            line,
            re.I
        )
        if experience:
            try:
              if bool(parser.parse(experience.groups()[0])):
                # print(experience.groups())
                exp_.append(experience.groups())
            except:
              continue
    # print(exp_)
    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return total_experience_in_months


def get_number_of_months_from_dates(date1, date2):
    '''
    Helper function to extract total months of experience from a resume
    :param date1: Starting date
    :param date2: Ending date
    :return: months of experience from date1 to date2
    '''
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = re.split(' |-|/',date1)
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = re.split(' |-',date2)
            date2 = date2[0][:3] + ' ' + date2[1]
        # print(date1)
        # print(date2)
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        # print(date1)
        # print(date2)
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience

def get_experience(document):
  exp = 0
  for word in document.ents:
    if word.label_ == "experience":
      # print(word.start_char, word.end_char, word.label_, doc.text[word.start_char:word.end_char])
      exp += get_total_experience(document.text[word.start_char:word.end_char].splitlines()) / 12
  return exp