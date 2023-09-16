import time
from selenium import webdriver
from bs4 import BeautifulSoup
from propertydata.models import Property  
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Scrape property data and save it to the database'

    def handle(self, *args, **options):
        base_url = "https://www.99acres.com/search/property/buy/"
        cities_and_localities = [
            ("hyderabad-all?city=38&preference=S&area_unit=1&res_com=R", "Hyderabad"),
            ("pune-all?city=18&preference=S&area_unit=1&res_com=R", "Pune, Maharashtra"),
            ("delhi-all?city=1&preference=S&area_unit=1&res_com=R", "Delhi, Delhi"),
            ("mumbai-all?city=3&preference=S&area_unit=1&res_com=R", "Mumbai, Maharashtra"),
            ("lucknow-all?city=128&preference=S&area_unit=1&res_com=R", "Lucknow, Uttar Pradesh"),
            ("agra-all?city=42&preference=S&area_unit=1&res_com=R", "Agra, Uttar Pradesh"),
            ("ahmedabad-all?city=11&preference=S&area_unit=1&res_com=R", "Ahmedabad, Gujarat"),
            ("kolkata-all?city=6&preference=S&area_unit=1&res_com=R", "Kolkata, West Bengal"),
            ("jaipur-all?city=40&preference=S&area_unit=1&res_com=R", "Jaipur, Rajasthan"),
            ("chennai-all?city=7&preference=S&area_unit=1&res_com=R", "Chennai, Tamil Nadu"),
            ("bangalore-all?city=10&preference=S&area_unit=1&res_com=R", "Bengaluru, Karnataka"),
        ]

        # Configure Selenium 
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu")  
        chrome_options.add_argument("--no-sandbox")  

        driver = webdriver.Chrome(options=chrome_options)

        for locality_url, city in cities_and_localities:
            url = f"{base_url}{locality_url}"
            driver.get(url)

            for _ in range(3):
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                time.sleep(2)  # Wait for the page to load

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            property_listings = soup.find_all("div", class_="srpWrap")

            for listing in property_listings:
                property_name = listing.find("div", class_="srpTuple__propertyName").text.strip()
                property_cost = listing.find("div", class_="srpTuple__price").text.strip()
                property_type = listing.find("div", class_="srpTuple__propType").text.strip()
                property_area = listing.find("div", class_="srpTuple__size").text.strip()
                property_locality = listing.find("span", class_="srpTuple__locName").text.strip()
                property_link = listing.find("a", class_="body_med")["href"]
                property_link = f"https://www.99acres.com{property_link}"

                property_data = Property(
                    property_name=property_name,
                    property_cost=property_cost,
                    property_type=property_type,
                    property_area=property_area,
                    property_locality=property_locality,
                    property_city=city,
                    property_link=property_link,
                )
                property_data.save()



        driver.quit()

        self.stdout.write(self.style.SUCCESS('Scraping and saving data completed successfully.'))
