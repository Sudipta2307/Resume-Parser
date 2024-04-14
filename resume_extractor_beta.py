import PyPDF2
from docx import Document
import re
import en_core_web_sm
import pdfplumber
import os

nlp = en_core_web_sm.load()
#Extract the text from pdf
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text
#Extraxt the text from word
def extract_text_from_word(file_path):
    doc = Document(file_path)
    text = " ".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def extract_name(text):
    lines = text.split('\n')
    for line in lines:
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line) or re.search(r'\(?\d{3}\)?[-.\s]??\d{3}[-.\s]??\d{4}', line):
            continue
        if len(line.split()) > 1 and re.search(r'[a-zA-Z]', line):
            return line
    return "Unknown"

def extract_email_from_resume(text):
    email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return email[0] if email else None

def extract_contact_number_from_resume(text):
    contact_number = []
    pattern = r"(\+\d{1,3}[-\.\s]?\d{1,4}[-\.\s]?\d{1,4}[-\.\s]?\d{1,4})|(\(\d{2,6}\)\s*\d{1,5}[-\.\s]*\d{1,5}[-\.\s]*\d{1,5})|(\d{3,5}[-\.\s]?\d{1,5}[-\.\s]?\d{1,5})"
    matches = re.findall(pattern, text)
    for match in matches:
        contact_number.append(''.join(re.findall(r'\d', ''.join(match))))
    return contact_number

def extract_education_from_resume(text):
    education = []
    education_keywords = [
        'Bachelor', 'B.Sc', 'B.A', 'B.Com', 'B.Tech', 'BEng', 'BArch',
        'Master', 'M.Sc', 'M.A', 'M.Com', 'M.Tech', 'MEng', 'MS',
        'PhD', 'DBA', 'DPhil',
        'Diploma', 'Certificate',
        'High School', 'SSC', 'HSC', '10th', '12th'
    ]
    for keyword in education_keywords:
        pattern = r"(?i)\b{}\b".format(re.escape(keyword))
        matches = re.findall(pattern, text)
        education.extend(matches)
    return list(set(education))

def extract_skills_from_resume(text, skills_list):
    escaped_skills = [re.escape(skill) for skill in skills_list]
    pattern = '|'.join(escaped_skills)
    skills = set(re.findall(pattern, text, re.IGNORECASE))
    return skills

def extract_job_data(text):
    doc = nlp(text)
    job_titles = []
    job_dates = []
    for ent in doc.ents:
        if ent.label_ == 'JOB_TITLE':
            job_titles.append(ent.text)
        elif ent.label_ == 'DATE':
            job_dates.append(ent.text)
    return job_titles, job_dates

def extract_resume_sections(text):
    education_section = extract_education_from_resume(text)
    skills_section = extract_skills_from_resume(text, [
        'Python', 'Java', 'C++', 'JavaScript', 'HTML', 'CSS', 'SQL',
        'React', 'Angular', 'Vue', 'Node.js', 'Express.js',
        'Django', 'Flask', 'Spring Boot',
        'MySQL', 'PostgreSQL', 'MongoDB',
        'AWS', 'GCP', 'Azure',
        'Docker', 'Kubernetes',
        'Git', 'SVN',
        'Agile', 'Scrum',
        'Machine Learning', 'Data Science', 'AI', 'Artificial Intelligence',
        'Deep Learning', 'Neural Networks',
        'NLP', 'Natural Language Processing',
        'Computer Vision',
        'Big Data', 'Hadoop', 'Spark',
        'Tableau', 'Power BI', 'Data Visualization',
        # Add more skills as needed
    ])
    job_titles, job_dates = extract_job_data(text)
    general_section = text

    return education_section, skills_section, job_titles, job_dates, general_section

def extract_job_titles(text):
    doc = nlp(text)
    job_titles = [ent.text for ent in doc.ents if ent.label_ == 'JOB_TITLE']
    return job_titles

def print_extracted_data(name, email, phone_number, education_section, skills_section, job_titles, job_dates, general_section):
    print("\n------------------- RESUME DETAILS -------------------")
    print(f"Name: {name}")

    if email:
        print(f"Email: {email}")

    if phone_number:
        print(f"Phone Number: {phone_number}")

    print("\n\nEducation Section:")
    for e in education_section:
        print(f"- {e}")

    print("\n\nSkills Section:")
    for s in skills_section:
        print(f"- {s}")

    print("\n\nJob Titles:")
    if job_titles:
        for title, date in zip(job_titles, job_dates):
            print(f"- {title} ({date})")
    else:
        print("No previous career.")

    print("\n\nGeneral Section:")
    print(general_section)

    print("\n\nCareer Trajectory:")
    if job_titles:
        trajectory = sorted(zip(job_titles, job_dates), key=lambda x: x[1])
        trajectory_str = " --> ".join([f"{title} ({date})" for title, date in trajectory])
        print(trajectory_str)
    else:
        print("No previous career.")

def main():
    folder_path = "resume_datasets/"
    file_name = input("\n\nPlease input the name of your resume file (e.g., sample_resume.pdf or sample_resume.docx): ")
    file_path = os.path.join(folder_path, file_name)
    text = ""
    if file_name.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_name.endswith('.docx'):
        text = extract_text_from_word(file_path)
    else:
        print("\nUnsupported file format. Please provide a PDF or DOCX file.")
        return

    name = extract_name(text)
    email = extract_email_from_resume(text)
    phone_number = extract_contact_number_from_resume(text)
    education_section, skills_section, job_titles, job_dates, general_section = extract_resume_sections(text)
    print_extracted_data(name, email, phone_number, education_section, skills_section, job_titles, job_dates, general_section)

if __name__ == "__main__":
    main()
