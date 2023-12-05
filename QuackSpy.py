import requests
import sys
import subprocess
from selenium import webdriver
from urllib.parse import urlparse
from time import sleep
from requests.exceptions import HTTPError
import os

def capture_screenshot(url, output_folder):
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(1)
    domain_name = urlparse(url).netloc.replace('.', '_').strip()
    screenshot_path = os.path.join(output_folder, domain_name + ".png")

    driver.get_screenshot_as_file(screenshot_path)
    driver.quit()

def howItLooksLike(f):
    with open(f, 'r') as file:
        domains = [line.strip() for line in file.readlines() if line.strip()]

    base_output_folder = 'captures'
    
    if not os.path.exists(base_output_folder):
        os.makedirs(base_output_folder)

    for domain in domains:
        capture_screenshot('https://' + domain, base_output_folder)
    
    print ("Captures of all the accessibles files saved in captures/")

def checkSites(f):
    with open(f, 'r') as file:
        pass

    with open("accessibles_sites.txt", 'w'):
        pass

    with open(f, 'r') as file:
        for ip in file:
            ip = ip.strip()
            if ip:
                try:
                    subprocess.run(['curl', '--max-time', '2', '-s', 'https://{}'.format(ip)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    with open("accessibles_sites.txt", 'a') as output_file:
                        output_file.write(ip + '\n')
                except subprocess.CalledProcessError:
                    pass
    print("File of accessibles sites saved")

def process_word(word):
    word = word.lower()
    word = word.replace('*.', '')
    word = word.replace('www.', '')
    return word.strip()

def process_file(input_file, output_file):
    unique_words = set()

    with open(input_file, 'r') as file:
        for line in file:
            words = line.split()
            processed_words = [process_word(word) for word in words]
            unique_words.update(processed_words)

    with open(output_file, 'w') as file:
        file.write('\n'.join(unique_words))

def get_subdomains(domain):
    try:
        response = requests.get("https://crt.sh/?q=.{}&output=json".format(domain))
        response.raise_for_status()
        
        jsonResponse = response.json()
        name_value = [None] * len(jsonResponse)
        for i in range(len(jsonResponse)):
            name_value[i] = jsonResponse[i]['common_name']
        name_value = set(name_value)
        file = open("all_subdomains.txt", "a")
        file.write("\n".join(name_value))
        process_file("all_subdomains.txt", "all_subdomains.txt")

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

if len(sys.argv) < 2:
    print("Please enter -f and a valid file")
    sys.exit(1)

if sys.argv[1] == "-f" and len(sys.argv) == 3:
    file = open(sys.argv[2], "r")
    for line in file:
        domain = line.strip()
        get_subdomains(domain)
    print("File saved as all_subdomains.txt") 
    checkSites("all_subdomains.txt")
    howItLooksLike("all_subdomains.txt")
    sys.exit(1)
else:
    print("Please enter a file name")