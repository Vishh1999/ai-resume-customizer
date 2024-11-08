import pandas as pd
import base64
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import fitz
import os
from fpdf import FPDF
from bs4 import BeautifulSoup
import time

# gemini key
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# Web Scraping
def scrape_webpage(url, company_name):
    # Initialize the WebDriver
    driver = webdriver.Chrome()

    # Navigate to the initial page that redirects to the SSO login
    driver.get(url)

    # Wait for the page to load
    time.sleep(3)

    # Locate the username and password fields
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")

    # Input credentials
    username = os.environ['PROFILE_USERNAME']
    password = base64.b64decode(os.environ['PROFILE_PASSWORD_base64']).decode("utf-8")
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Submit the form
    password_input.send_keys(Keys.RETURN)

    # Complete the Duo approval on phone
    time.sleep(10)

    # click the Yes, this is my Device button
    button = driver.find_element(By.ID, "trust-browser-button")
    button.click()  # Click the button

    # Wait for the login to complete and the target page to load
    time.sleep(10)

    # After login, access the page source
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Close the browser
    driver.quit()

    # Now you can proceed with BeautifulSoup to find specific elements
    company_name = company_name
    job_role = soup.title.get_text()
    job_details = soup.find("div", {"class": 'job-details-body'}).text.strip()
    end_date = soup.find("strong").get_text(strip=True)
    return {"company_name": company_name,
            "job_role": job_role, "job_details": job_details, "end_date": end_date,
            "applied": False}

# Function to generate customized resume and cover letter using OpenAI API
def generate_documents(base_resume_text, job_details):
    # Combine the base resume and job details as input for the LLM
    prompt = f"Based on the following base resume:\n\n{base_resume_text}\n\nand the job details:\n\n{job_details}\n\n" \
             "Generate a customized CV and cover letter tailored to the job. Format the output as:\n\n" \
             "Customized CV:\n[Your customized CV here]\n\nCustomized Cover Letter:\n[Your customized cover letter here]"

    # Generate response from the genAI API
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Split the response text to separate CV and cover letter
    response_text = response.text.strip()
    cv_text, cover_letter_text = response_text.split("Customized Cover Letter:")

    return cv_text.strip("Customized CV:"), cover_letter_text.strip()


# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


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


# Example usage with a URL of a job posting
url = input("Please post URL of career connect")
company_name = input("Please input the company name!")

# Scrape the webpage
web_data = scrape_webpage(url, company_name)
# Print a snippet for verification
print(f"Scraped Job Title: {web_data['job_role']}\nDescription: {web_data['job_details'][:10]}...")

# Save metadata to CSV
with open('UK_jobs/job_applications.csv', 'a') as f:
    f.write('\n')
df = pd.DataFrame([web_data])
df.to_csv("UK_jobs/job_applications.csv", mode='a', header=False)
print("Data saved to the CSV.")

# read the base resume pdf
base_resume_text = extract_text_from_pdf("UK_jobs/Vishak_L_V_base_resume.pdf")

# Generate customized resume and cover letter
customized_cv, customized_cover_letter = generate_documents(base_resume_text,
                                                            web_data['job_details'])

# Save the customized CV and cover letter as PDFs
save_text(customized_cv, f"UK_jobs/Customized_CV_{company_name}.txt")
save_text(customized_cover_letter, f"UK_jobs/Customized_Cover_Letter_{company_name}.txt")
print("Customized CV and Cover Letter have been saved as PDFs.")