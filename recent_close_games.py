import json
from random import shuffle
import requests
from datetime import date, timedelta
from PyInquirer import prompt
from prompt_toolkit.validation import ValidationError
from nba_teams import nba_teams_data

last_week = (date.today() - timedelta(weeks=1)).isoformat()
nba_teams = [team["teamName"] for team in nba_teams_data]

print(nba_teams)


def dateValidation(d: str):
    try:
        date.fromisoformat(d)
    except ValueError:
        raise ValidationError(0, message="Please enter a valid date in yyyy-MM-dd")
    else:
        return True


def scoreDiffValidation(s: str):
    try:
        diff = int(s)
        if diff <= 0:
            raise ValidationError(0, message="Invalid score diff")
    except ValueError:
        raise ValidationError(0, message="Invalid score diff")
    else:
        return True


def teamsValidation(t: str):
    if t == "":
        return True

    teams = t.split(",")

    for team in teams:
        if team not in nba_teams:
            raise ValidationError(0, message=f"Invalid nba team {team}")

    return True


questions = [
    {
        'type': 'input',
        'name': 'start_date',
        'message': f'Start date:',
        'default': last_week,
        'validate': lambda i: dateValidation(i)
    },
    {
        'type': 'input',
        'name': 'threshold',
        'message': 'Max score difference:',
        'default': '5',
        'validate': lambda s: scoreDiffValidation(s)
    },
    {
        'type': 'input',
        'name': 'team',
        'message': 'Teams (comma-separated):',
        'default': '',
        'validate': lambda t: teamsValidation(t)
    }
]


def getGamesFromDate(start_date: str, teams):
    params = {"start_date": start_date, "per_page": 100}

    res = requests.get("https://www.balldontlie.io/api/v1/games", params=params).json()
    meta = res["meta"]

    total_pages = meta["total_pages"]

    all_games = []

    for page in range(total_pages):
        page_num = page + 1
        page_request_params = params.copy()
        page_request_params["page"] = page_num

        print(f"Processing page {page_num} of {total_pages}...", end="\r")
        page_res = requests.get("https://www.balldontlie.io/api/v1/games", params=page_request_params).json()
        page_data = page_res["data"]

        if teams != [""]:
            page_data = list(filter(lambda x: x["home_team"]["full_name"] in teams or x["visitor_team"]["full_name"] in teams, page_data))

        all_games.extend(page_data)

    return all_games


def getCloseGamesFromDate(start_date: str, teams, threshold=5):
    all_games = getGamesFromDate(start_date, teams)
    difference_between = lambda x, y: abs(int(x) - int(y))
    close_games = [game for game in all_games if
                   game["status"] == "Final" and
                   difference_between(game["home_team_score"], game["visitor_team_score"]) < threshold]

    return close_games


if __name__ == "__main__":
    answers = prompt(questions)
    start_date: str = answers["start_date"]
    threshold: int = int(answers["threshold"])
    teams: list[str] = answers["team"].split(",")

    close_games = getCloseGamesFromDate(start_date, teams, threshold)
    sorted_close_games = sorted(close_games, key=lambda game: game["date"])

    if len(sorted_close_games) == 0:
        print("No games found")

    for game in sorted_close_games:
        game_date = game["date"][:10]  # get only date
        home_team = game["home_team"]["full_name"]
        home_team_score = game["home_team_score"]
        visitor_team = game["visitor_team"]["full_name"]
        visitor_team_score = game["visitor_team_score"]
        scores = [visitor_team_score, home_team_score]
        shuffle(scores)

        print(f'{game_date}\t{home_team} vs {visitor_team}: {scores[0]} - {scores[1]}')
