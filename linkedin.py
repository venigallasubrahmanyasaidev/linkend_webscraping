# Linkedin job link and job description webscraping 
# 1st step need to webscrap the all job links 
# 2nd step from that link need to ectract the all the information

# packages required 
# BeautifulSoup : pip install requests beautifulsoup4
# selenium      :pip install selenium
# panadas       :pip install pandas
# requests      :pip install requests
# webdriver-manager :pip install webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd  
# here im using chrome webdrivers to open the link from chrome
chromedriver_path = 'chromedriver.exe' 


service = Service(chromedriver_path)
options = webdriver.ChromeOptions()


driver = webdriver.Chrome(service=service, options=options)

def scrape_linkedin_jobs(search_term, location):
    base_url = 'https://www.linkedin.com/jobs/search/' # here urls breaks into three parts this is base url
    driver.get(f'{base_url}?keywords={search_term}&location={location}') # we can give what job description we want and location 
    jobs = []
    wait = WebDriverWait(driver, 20)  
    print("Navigated to LinkedIn jobs page.")
    # here after opening the link in chrome to scrape the all links from the job posts
    last_height = driver.execute_script("return document.body.scrollHeight") 
    print("last_height:",last_height)
    
    while True:
        try:
            # here in this xpath there are list of job 
            job_listings = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="main-content"]/section/ul/li')))  
            print(f"Found {len(job_listings)} job listings on the page.")
        except Exception as e:
            print(f"Error locating job listings: {e}")
            break

        for job in job_listings:
            try:
                # after getting list of job  by the class name getting the text from there 
                job_title = job.find_element(By.CLASS_NAME, 'sr-only').text
                company_name = job.find_element(By.CLASS_NAME, 'base-search-card__subtitle').text
                location = job.find_element(By.CLASS_NAME, 'job-search-card__location').text
                # here converting the post time intlo date formate 
                # for example here posted 2 hours ago means compare with current data and time calculate the time
                if "ago" in job.find_element(By.XPATH, './div/div[2]/div/time').text:
                    hours = int(job.find_element(By.XPATH, './div/div[2]/div/time').text.split()[0])
                    posted_time = datetime.now()-timedelta(hours=hours)
                # here there is link of that job using class name getting the link of the job to extract company name,loaction, job description ,..etc
                job_link = job.find_element(By.CLASS_NAME, 'base-card__full-link').get_attribute('href')

                print(f"Scraped job: {job_title} at {company_name} in {location}, posted {posted_time}")

                jobs.append({
                    'Job Title': job_title,
                    'Company Name': company_name,
                    'Location': location,
                    'Posted Time': posted_time,
                    'Job Link': job_link
                })
            except Exception as e:
                print(f"Error extracting job details: {e}")
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the end of the page.")
            break
        last_height = new_height

    driver.quit()
    return jobs


search_term = 'Data Scientist'  
location = 'Bengaluru'
jobs = scrape_linkedin_jobs(search_term, location)

if jobs:
    df = pd.DataFrame(jobs)
    df.to_csv('linkedin_jobs.csv', index=False) # here in the csv formate 
    print("Scraping completed and data saved to linkedin_jobs.csv")
else:
    print("No jobs were scraped.")

# after save links in csv fromate 
# we need to extract information from each and every link 
def scrape_linkedin_job(job_link):# each and every link csv will call this function only by one
    try:
        response = requests.get(job_link) 
        soup = BeautifulSoup(response.text, 'html.parser')
      
        job_title_element = soup.find('h1', class_='top-card-layout__title') 
        job_title = job_title_element.text.strip() if job_title_element else 'N/A' # using this getting the job role 

        # here getting the details like organiztion name,loaction  from those classes 
        org_element = soup.find('h4', class_='top-card-layout__second-subline')
        org_name_element = org_element.find('a', class_='topcard__org-name-link')
        org_name = org_name_element.text.strip() if org_name_element else 'N/A'  
        location = org_element.find('span', class_='topcard__flavor--bullet').text.strip() if org_element.find('span', class_='topcard__flavor--bullet') else 'N/A'


        description_sections = soup.find_all('div', class_='show-more-less-html__markup') # save getting the all information from html page   
        # above details are saving in the dictionary  
        sections = {
            'job_title': job_title,
            'organization': org_name,
            'location': location,
        }

        # from description_sections need to extract the details with span tag 
        for section in description_sections:
            section_title = section.find_previous('span') # finding the span tag
            if section_title:
              
                section_title_text = section_title.text.strip() 
    
                section_content = section.get_text(separator="\n\n").strip() # selections are separated 
                if section_title_text in sections:
                    sections[section_title_text] += section_content # here adding above dictionary with title and the text 
                    print('')
                else:
                    sections[section_title_text] = section_content

        return sections
    except Exception as e:
        print(f"Error scraping job: {e}")
        return None


csv_file_path = 'linkedin_jobs.csv'  # reading csv file
df = pd.read_csv(csv_file_path) #storing in df 


if 'Job Link' not in df.columns:
    print("The CSV file does not contain a 'Job Link' column.")
else:
    job_links = df['Job Link'].dropna().tolist()
    for job_link in job_links:
        job_data = scrape_linkedin_job(job_link) # for each job link it will call scrape_linkedin_job function
        if job_data: # if return sections having any data means printing that
            for key, value in job_data.items():
                print(f"{key}:{value}\n") 
            print("="*40)  
        else:
            print("Failed to scrape job data.")
        time.sleep(10)  


"""Here there is a extened code , just i was printing a block of words using python but here need to add NLP and regular exprestions to extract the information 
clear so i starting learning NLP """