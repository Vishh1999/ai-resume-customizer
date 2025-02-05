import pandas as pd
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from bs4 import BeautifulSoup
import time

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
    job_role = job_role.replace("- Careers & Employability Service", '')
    job_details = soup.find("div", {"class": 'job-details-body'}).text.strip()
    job_details = job_details.replace("About this role", '')
    end_date = soup.find("strong").get_text(strip=True)
    return {"company_name": company_name,
            "job_role": job_role, "job_details": job_details, "end_date": end_date,
            "applied": False}


# Example usage with a URL of a job posting
url = input("Please post URL of career connect: ")
company_name = input("Please input the company name: ")

# Scrape the webpage
web_data = scrape_webpage(url, company_name)
web_data['url'] = url
# Print a snippet for verification
print(f"Scraped Job Title: {web_data['job_role']}\nDescription: {web_data['job_details'][:10]}...")

# Save metadata to JSON
df = pd.DataFrame([web_data])
existing_df = pd.read_json('UK_jobs/UK_job_applications.json')
new_df = pd.concat([existing_df, df])
# sort the df based on end_date
new_df['end_date_2'] = pd.to_datetime(new_df['end_date'], format='%d-%b-%Y')
new_df = new_df.sort_values(by=['applied', 'end_date_2'])
new_df.drop('end_date_2', inplace=True, axis=1)

new_df.to_json("UK_jobs/UK_job_applications.json", orient='records', indent=2)

print("Data saved to the JSON.")
