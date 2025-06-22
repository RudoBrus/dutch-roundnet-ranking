import csv
import re
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

INPUT_FILE = Path(__file__).parent / "tournaments.csv"
OUTPUT_DIRECTORY = Path(__file__).parent.parent.joinpath(
    "ranking_calculator/tournament_data"
)


def extract_date(driver: webdriver.Chrome) -> datetime | None:
    date_element = driver.find_elements(By.CLASS_NAME, "date")
    if date_element:
        for element in date_element:
            cleaned_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", element.text)
            return datetime.strptime(cleaned_date, "%B %d, %Y")
    print("No date element found, the tournament is probably in the future!")
    return None


def open_dropdown(driver: webdriver.Chrome) -> None:
    try:
        divisions_dropdown = driver.find_element(
            By.CLASS_NAME, "select-input-container"
        )
        divisions_dropdown.click()
    except NoSuchElementException as e:
        print(f"Dropdown element not found: {e}")


def find_teams_in_division(
    driver: webdriver.Chrome, max_wait_time: int = 20
) -> list[dict[str, str]]:
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
                f"Results of tournament are not yet published! "
                f"Tournament: {driver.current_url}"
            )
            return []

        if player_elements:
            players_in_division = []
            for rank, players in enumerate(player_elements):
                player1, player2 = players.text.split(" and ")
                players_in_division.append(
                    {"name": player1.title(), "rank": str(rank + 1)}
                )
                players_in_division.append(
                    {"name": player2.title(), "rank": str(rank + 1)}
                )
            return players_in_division
        print("No players found")
        return []
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Empty division\nError: {e}")
        return []


def find_divisions(driver: webdriver.Chrome) -> dict[str, str]:
    open_dropdown(driver)
    divisions = driver.find_elements(
        By.XPATH, "//*[contains(@id, 'react-select') and contains(@id, '-option-')]"
    )
    return {
        div_id: div.text
        for div in divisions
        if (div_id := div.get_attribute("id")) is not None
    }


def select_division(division_name: str) -> str:
    if "women" in division_name.lower():
        return "women"
    if "advanced" in division_name.lower():
        return "advanced"
    if "intermediate" in division_name.lower():
        return "intermediate"
    if "beginner" in division_name.lower():
        return "beginner"
    return "unknown"


def create_tournament_data(driver: webdriver.Chrome) -> list[dict[str, str]] | None:
    divisions = find_divisions(driver)
    all_players = []
    for division_id, division_name in divisions.items():
        print(f"Scraping division: {division_name}\n")
        div = driver.find_element(By.ID, division_id)
        div.click()

        teams = find_teams_in_division(driver)
        if teams:
            division = select_division(division_name)
            for team in teams:
                team["category"] = division
            all_players.extend(teams)

        open_dropdown(driver)
    return all_players if all_players else None


def save_tournament_data(
    tournament_date: datetime,
    tournament_name: str,
    tournament_data: list[dict[str, str]],
) -> None:
    filename = (
        OUTPUT_DIRECTORY.joinpath(
            f"{tournament_date.strftime('%Y-%m-%d')}_{tournament_name}.csv"
        )
        .absolute()
        .as_posix()
    )
    print("Saving file in: ", filename)
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "rank", "category"])
        writer.writeheader()
        writer.writerows(tournament_data)


def create_selenium_driver() -> webdriver.Chrome:
    try:
        service = Service(executable_path="/usr/local/bin/chromedriver")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--incognito")
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(20)  # Set implicit wait time for elements to load
        print("Chrome WebDriver started successfully.")
        return driver
    except Exception as e:
        print(f"Error starting WebDriver: {e}")
        raise


def get_tournaments_to_scrape() -> list[dict[str, str]]:
    with open(INPUT_FILE.as_posix(), encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            {"location": row["location"], "url": row["url"]}
            for row in reader
            if row["already_scraped"].lower() == "false"
            and row["results_published"].lower() == "true"
        ]


def scrape_tournaments(
    driver: webdriver.Chrome, tournaments: list[dict[str, str]]
) -> None:
    for tournament in tournaments:
        print("\n" + "*" * 75 + "\n")
        print(f"Start scraping of: {tournament['url']}\n")

        try:
            driver.get(tournament["url"])
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Couldn't open this url: {tournament['url']}, error: {e}")
            continue

        date = extract_date(driver)
        if not date or date > datetime.today():
            print("Tournament is in the future!")
            print("Tournament date: ", date)
            continue
        print("Tournament date: ", date, "\n")

        results_url = f"{tournament['url']}/results"
        driver.get(results_url)

        all_player_rankings = create_tournament_data(driver)
        if all_player_rankings:
            print(all_player_rankings)
            save_tournament_data(date, tournament["location"], all_player_rankings)


if __name__ == "__main__":
    selenium_driver = create_selenium_driver()
    tournaments_to_scrape = get_tournaments_to_scrape()
    scrape_tournaments(selenium_driver, tournaments_to_scrape)
    selenium_driver.quit()
