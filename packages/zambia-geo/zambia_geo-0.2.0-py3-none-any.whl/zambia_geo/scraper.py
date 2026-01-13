import requests
from bs4 import BeautifulSoup
from pprint import pformat
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://www.parliament.gov.zm/members/constituencies"


def scrape_zambia_constituencies():
    response = requests.get(URL, timeout=30, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    data = {}

    for province_heading in soup.select("div.view-content > h3"):
        province = province_heading.get_text(strip=True)

        table = province_heading.find_next_sibling("table")
        if not table:
            continue

        constituencies = []
        for link in table.select("a"):
            name = link.get_text(strip=True)
            if name:
                constituencies.append(name)

        data[province] = constituencies

    return data


if __name__ == "__main__":
    constituencies = scrape_zambia_constituencies()

    # Write as a Python dict
    with open("zambia_constituencies.py", "w", encoding="utf-8") as f:
        f.write("# Auto-generated file. Do not edit manually.\n\n")
        f.write("ZAMBIA_CONSTITUENCIES = ")
        f.write(pformat(constituencies, width=120))
        f.write("\n")

    print("Saved to zambia_constituencies.py")
