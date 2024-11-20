# ----------------------------------------------------------#
# Licensed under the GNU Affero General Public License v3.0 #
# ----------------------------------------------------------#

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

class EarthquakeWrapper:
    def __init__(self):
        self.base_url = "https://www.data.jma.go.jp/multi/quake/index.html?lang=en"

    def get_earthquakes(self):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get(self.base_url)
        # Wait for 5 seconds
        time.sleep(3)
        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        table = soup.find_all("table", {"id": "quakeindex_table"})
        if len(table) != 1:
            return None
        table_soup = BeautifulSoup(str(table[0]), "html.parser")
        table_body = table_soup.find_all("tbody")
        if len(table_body) != 1:
            return None
        table_body_soup = BeautifulSoup(str(table_body[0]), "html.parser")
        table_rows = table_body_soup.find_all("tr")
        earthquakes = []
        for row in table_rows[1:]:
            row_soup = BeautifulSoup(str(row), "html.parser")
            row_data = row_soup.find_all("td")
            row_data = [str(item) for item in row_data]
            for index, item in enumerate(row_data):
                current_item = item.replace("<td>", "")
                current_item = current_item.replace("</td>", "")
                row_data[index] = current_item
            earthquakes.append(
                {
                    "epicenter_location": row_data[1],
                    "magnitude": row_data[2],
                    "max_seismic_intensity": row_data[3],
                    "issue_time": row_data[4]
                }
            )
        return earthquakes
