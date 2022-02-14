from datetime import date, timedelta
from random import shuffle
import requests
from datetime import date, timedelta

def getGamesFromDate(startDate: date):
    params = { "start_date": startDate.isoformat(), "per_page": 100 }
    
    res = requests.get("https://www.balldontlie.io/api/v1/games", params=params).json()
    meta = res["meta"]
    
    total_pages = meta["total_pages"]
    
    all_games = []
    
    for page in range(total_pages):
        page_num = page + 1
        page_request_params = params.copy()
        page_request_params["page"] = page_num
        
        page_res = requests.get("https://www.balldontlie.io/api/v1/games", params=page_request_params).json()
        page_data = page_res["data"]
        all_games.extend(page_data)
        
    return all_games

def getCloseGamesFromDate(startDate: date):
    all_games = getGamesFromDate(startDate)
    difference_between = lambda x,y: abs(int(x)-int(y))
    close_games = [game for game in all_games if game["status"] == "Final" and difference_between(game["home_team_score"], game["visitor_team_score"]) < 10]   
    
    return close_games



if __name__ == "__main__":
    last_week = date.today() - timedelta(weeks=1)
    close_games = getCloseGamesFromDate(last_week)

    for game in close_games:
        home_team = game["home_team"]["full_name"]
        home_team_score = game["home_team_score"]
        visitor_team = game["visitor_team"]["full_name"]
        visitor_team_score = game["visitor_team_score"]
        scores = [visitor_team_score, home_team_score]
        shuffle(scores)

        print(f'{home_team} vs {visitor_team}: {scores[0]} - {scores[1]}')