import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

INPUT_DIRECTORY = Path(__file__).parent
OUTPUT_DIRECTORY = Path(__file__).parent.parent.joinpath(
    "ranking_calculator/tournament_data"
)


def extract_date(driver):
    # Find date element
    date_element = driver.find_elements(By.CLASS_NAME, "date")

    if date_element is not None:
        for element in date_element:
            # Convert to datetime format
            cleaned_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", element.text)
            date = datetime.strptime(cleaned_date, "%B %d, %Y")
            return date
    else:
        print("No date element found, the tournament is probably in the future!")
        return None


def open_dropdown(driver):
    try:
        divisions_dropdown = driver.find_element(
            By.CLASS_NAME, "select-input-container"
        )
        divisions_dropdown.click()
        # print("Opened dropdown succesfully")
    except:
        print("Couldn't open dropdown menu")

    return


def find_teams_in_division(driver, max_wait_time=20):
    try:
        # print('Start search')
        player_elements = WebDriverWait(driver, max_wait_time).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "players"))
        )
        rankings_published = WebDriverWait(driver, max_wait_time).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "title"))
        )

        published = False
        for tit in rankings_published:
            if "Final" in tit.text:
                published = True
            elif "Results" in tit.text:
                print(
                    f"Results of tournament are not yet published! Tournament: {str(driver.current_url)}\n"
                )
                return None

        if not published:
            print(
                f"Results of tournament are not yet published! Tournament: {str(driver.current_url)}\n"
            )
            return None

        if player_elements:
            players_in_division = []
            for rank, players in enumerate(player_elements):
                player1, player2 = players.text.split(" and ")
                players_in_division.append([player1.title(), rank + 1])
                players_in_division.append([player2.title(), rank + 1])
                # print(rank+1, player1, player2)

            if len(players_in_division) > 0:
                return pd.DataFrame(players_in_division, columns=["name", "rank"])
            return None
        print("No players found")
        return None
    except:
        print("Empty division\n")
        return None

    message_elements = driver.find_elements(By.CLASS_NAME, "message")
    for message in message_elements:
        print(message.text)


def find_divisions(driver, waittime=20):
    driver.implicitly_wait(waittime)
    divisions = driver.find_elements(
        By.XPATH, "//*[contains(@id, 'react-select') and contains(@id, '-option-')]"
    )

    division_ids = [div.get_attribute("id") for div in divisions]
    division_names = [div.text for div in divisions]

    return division_ids, division_names


def select_division(division_name):
    if "women" in division_name.lower():
        return "womens"
    if "advanced" in division_name.lower():
        return "advanced"
    if "intermediate" in division_name.lower():
        return "intermediate"
    if "beginner" in division_name.lower():
        return "beginner"
    return "advanced"


def create_tournament_dataframe(driver, division_ids, waittime=20):
    all_players = []
    for div_id in division_ids:
        div = driver.find_element(By.ID, div_id)
        text = div.text
        print(f"Scraping division: {text}\n")
        div.click()
        driver.implicitly_wait(waittime)

        teams = find_teams_in_division(driver)

        if teams is not None:
            teams["category"] = select_division(text)

            all_players.append(teams)

        open_dropdown(driver)
    if all_players:
        return pd.concat(all_players)
    print(
        "Something went wrong collecting the ranked data, probably none of the divisions have published results."
    )
    return None


def save_tournament_dataframe(date, tournament_dataframe):
    filename = (
        OUTPUT_DIRECTORY.joinpath(f"{date.strftime('%Y-%m-%d')}.csv")
        .absolute()
        .as_posix()
    )
    print("Saving file in: ", filename)
    tournament_dataframe.to_csv(filename, index=False)


def scrape_fwango_tournaments(waittime=20, max_wait_time=1):
    # Set up Geckodriver service
    service = Service(
        executable_path="/home/rens/miniconda3/envs/fwango/bin/geckodriver"
    )  # Update with the correct path

    # Set Firefox options
    options = Options()
    options.binary_location = "/usr/bin/firefox"  # Update if needed
    options.add_argument("-headless")  # Optional: Run in headless mode

    # Initialize WebDriver
    driver = webdriver.Firefox(service=service, options=options)

    # Read which fwango url's are requested
    inputfile = INPUT_DIRECTORY.joinpath("tournament_url.txt")

    with open(inputfile.absolute().as_posix()) as f:
        urls = [line.rstrip() for line in f]

    # Loop through all requested urls
    for url in urls:
        print("\n")
        print("*" * 75)
        print("\n")
        print(f"Start scraping of: {url}\n")

        # Check for corrupt links and skips
        if "fwango" not in url:
            print(f"Skipping line containing '{url}', because it is not a fwango url!")
            continue
        if "skip" in url[0:4]:
            print(f"Skipping line containing '{url}'")
            continue

        # Open the fwango page
        try:
            driver.get(url)
        except:
            print(f"Couldn't open this url: {url}")
            continue

        # Wait for elements to load
        driver.implicitly_wait(waittime)

        # Find tournament date
        date = extract_date(driver)
        if date is None:
            continue
        if date > datetime.today():
            print("Tournament is in the future!")
            print("Tournament date: ", date)
            continue
        print("Tournament date: ", date, "\n")

        # Open the results page
        results_url = f"{url}/results"
        driver.get(results_url)
        driver.implicitly_wait(waittime)

        # Find divisions
        open_dropdown(driver)
        division_ids, division_names = find_divisions(driver)

        # Scrape player rankings from all divisions
        all_player_rankings = create_tournament_dataframe(driver, division_ids)
        if all_player_rankings is not None:
            print(all_player_rankings)

            # Save tournament ranking if it is available
            save_tournament_dataframe(date, all_player_rankings)

    # Close browser
    driver.quit()


if __name__ == "__main__":
    scrape_fwango_tournaments()
