import csv
import re
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

INPUT_DIRECTORY = Path(__file__).parent
OUTPUT_DIRECTORY = Path(__file__).parent.parent.joinpath(
    "ranking_calculator/tournament_data"
)


def extract_date(driver):
    date_element = driver.find_elements(By.CLASS_NAME, "date")
    if date_element:
        for element in date_element:
            cleaned_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", element.text)
            date = datetime.strptime(cleaned_date, "%B %d, %Y")
            return date
    print("No date element found, the tournament is probably in the future!")
    return None


def open_dropdown(driver):
    try:
        divisions_dropdown = driver.find_element(
            By.CLASS_NAME, "select-input-container"
        )
        divisions_dropdown.click()
    except:
        print("Couldn't open dropdown menu")


def find_teams_in_division(driver, max_wait_time=20):
    try:
        player_elements = WebDriverWait(driver, max_wait_time).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "players"))
        )
        rankings_published = WebDriverWait(driver, max_wait_time).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "title"))
        )

        published = any("Final" in tit.text for tit in rankings_published)
        if not published:
            print(
                f"Results of tournament are not yet published! Tournament: {driver.current_url}\n"
            )
            return None

        if player_elements:
            players_in_division = []
            for rank, players in enumerate(player_elements):
                player1, player2 = players.text.split(" and ")
                players_in_division.append({"name": player1.title(), "rank": rank + 1})
                players_in_division.append({"name": player2.title(), "rank": rank + 1})
            return players_in_division if players_in_division else None
        print("No players found")
        return None
    except:
        print("Empty division\n")
        return None


def find_divisions(driver, waittime=20):
    driver.implicitly_wait(waittime)
    divisions = driver.find_elements(
        By.XPATH, "//*[contains(@id, 'react-select') and contains(@id, '-option-')]"
    )
    division_ids = [div.get_attribute("id") for div in divisions]
    division_names = [div.text for div in divisions]
    return division_ids, division_names


def select_division(division_name):
    if "womens" in division_name.lower():
        return "women"
    if "advanced" in division_name.lower():
        return "advanced"
    if "intermediate" in division_name.lower():
        return "intermediate"
    if "beginner" in division_name.lower():
        return "beginner"
    return "advanced"


def create_tournament_data(driver, division_ids, waittime=20):
    all_players = []
    for div_id in division_ids:
        div = driver.find_element(By.ID, div_id)
        text = div.text
        print(f"Scraping division: {text}\n")
        div.click()
        driver.implicitly_wait(waittime)

        teams = find_teams_in_division(driver)
        if teams:
            division = select_division(text)
            for team in teams:
                team["category"] = division
            all_players.extend(teams)

        open_dropdown(driver)
    return all_players if all_players else None


def save_tournament_data(tournament_date, tournament_name, tournament_data):
    filename = (
        OUTPUT_DIRECTORY.joinpath(
            f"{tournament_date.strftime('%Y-%m-%d')}_{tournament_name}.csv"
        )
        .absolute()
        .as_posix()
    )
    print("Saving file in: ", filename)
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "rank", "category"])
        writer.writeheader()
        writer.writerows(tournament_data)


def create_selenium_driver():
    try:
        service = Service(executable_path="/usr/local/bin/chromedriver")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--incognito")
        driver = webdriver.Chrome(service=service, options=options)
        print("Chrome WebDriver started successfully.")
        return driver
    except Exception as e:
        print(f"Error starting WebDriver: {e}")
        raise


def scrape_fwango_tournaments(waittime=20, max_wait_time=1):
    driver = create_selenium_driver()
    inputfile = INPUT_DIRECTORY.joinpath("tournament_urls.csv")

    with open(inputfile.absolute().as_posix()) as f:
        reader = csv.DictReader(f)
        tournaments = [
            {"location": row["location"], "url": row["url"], "skip": row["skip"]}
            for row in reader
            if "fwango" in row["url"] and row["skip"].lower() != "false"
        ]

    for tournament in tournaments:
        print("\n" + "*" * 75 + "\n")
        print(f"Start scraping of: {tournament['url']}\n")

        try:
            driver.get(tournament["url"])
        except:
            print(f"Couldn't open this url: {tournament['url']}")
            continue

        driver.implicitly_wait(waittime)
        date = extract_date(driver)
        if not date or date > datetime.today():
            print("Tournament is in the future!")
            print("Tournament date: ", date)
            continue
        print("Tournament date: ", date, "\n")

        results_url = f"{tournament['url']}/results"
        driver.get(results_url)
        driver.implicitly_wait(waittime)

        open_dropdown(driver)
        division_ids, division_names = find_divisions(driver)
        all_player_rankings = create_tournament_data(driver, division_ids)
        if all_player_rankings:
            print(all_player_rankings)
            save_tournament_data(date, tournament["location"], all_player_rankings)

    driver.quit()


if __name__ == "__main__":
    scrape_fwango_tournaments()
