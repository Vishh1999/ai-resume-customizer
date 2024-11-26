from fpdf import FPDF
import pandas as pd
import google.generativeai as genai
import fitz
import os

# gemini key
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    return text


# Function to generate customized resume and cover letter using GenAI API
def generate_documents(base_resume_text, company_name, job_role, job_details):
    # read the example data for the detailed prompt
    with open('UK_jobs/example_job_details.txt', 'r') as f:
        example_job_details = f.read()

    with open('UK_jobs/example_answer.txt', 'r') as f:
        example_answer = f.read()

    # Combine the base resume and job details as input for the LLM
    prompt = f"""
    Based on the,  
    base resume text: \n\n {base_resume_text}, \n\n
    company name: \n\n {company_name}, \n\n
    job role: \n\n {job_role}, \n\n
    job details: \n\n {job_details}. \n\n
    
    Please generate a custom CV and cover letter by tailoring the base resume text using the provided 
    company name, job role and job details.
    Format the output as:\n\n Customized CV:\n[Your customized CV text here]\n\n
    Customized Cover Letter:\n[Your customized cover letter text here]
    
    Ex: 
    base resume text: \n\n {base_resume_text}, \n\n
    company name: \n\n British Airways, \n\n
    job role: \n\n Summer Internships, \n\n
    job details: \n\n {example_job_details}, \n\n
    
    Expected result is, 
    {example_answer}
    """
    print(prompt)
    # Generate response from the genAI API
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Split the response text to separate CV and cover letter
    response_text = response.text.strip()
    cv_text, cover_letter_text = response_text.split("Customized Cover Letter:")

    return cv_text.strip("Customized CV:"), cover_letter_text.strip()

# Function to save text content to a PDF file
def save_text_to_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in text.splitlines():
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output(filename)


# Function to save text content to .txt file
def save_text(text, filename):
    with open(filename, mode='w') as output:
        output.write(text)


# read the full list of all the jobs
job_df = pd.read_json("UK_jobs/UK_job_applications.json")

# sort the df based on end_date and not applied
job_df['end_date_2'] = pd.to_datetime(job_df['end_date'], format='%d-%b-%Y')
job_df = job_df.sort_values(by=['applied', 'end_date_2'])
job_df.drop('end_date_2', inplace=True, axis=1)

# select the job and role for which the documents are to be created
for job, role in zip(job_df['company_name'].to_list(), job_df['job_role'].to_list()):
    print(f"'{job}' -- '{role}'")

company_name = input("input the company name for which the documents are to be created: ")
job_role = input("input the job_role for the company chosen: ")
job_details = job_df[(job_df['company_name'] == company_name) &
                     (job_df['job_role'] == job_role)]['job_details'].iloc[0]

# read the base resume pdf
base_resume_text = extract_text_from_pdf("UK_jobs/Vishak_UK_CV_SW.pdf")

# Generate customized resume and cover letter
customized_cv, customized_cover_letter = generate_documents(base_resume_text, company_name,
                                                            job_role, job_details)

# Save the customized CV and cover letter as PDFs
save_text(customized_cv, f"UK_jobs/Customized_CV_{company_name}.txt")
save_text(customized_cover_letter, f"UK_jobs/Customized_Cover_Letter_{company_name}.txt")
print("Customized CV and Cover Letter have been saved as text files.")