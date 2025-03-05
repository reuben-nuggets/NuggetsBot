from nba_api.stats.endpoints import playercareerstats, teamgamelog, boxscoretraditionalv3
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.static.teams import find_team_by_abbreviation
import pandas
import json
import requests

average_stats = {}

def get_previous_stats():
    team = teamgamelog.TeamGameLog(1610612743)
    most_recent_games = team.get_data_frames()[0].iloc[1:11]
    pts = 0
    fg_pct = 0
    for i, r in most_recent_games.iterrows():
        pts += r["PTS"]
        fg_pct += r["FG_PCT"] * 100
    pts = pts / 10
    fg_pct = fg_pct / 10
    return {"avg_pts_past_10":pts, "avg_fg_past_10":fg_pct}

previous_stats = get_previous_stats()

team = teamgamelog.TeamGameLog(1610612743)
most_recent_game = team.get_data_frames()[0].iloc[0]
boxscores = boxscoretraditionalv3.BoxScoreTraditionalV3(most_recent_game.Game_ID)
game_date = most_recent_game.GAME_DATE
opp_team_abb = most_recent_game.MATCHUP.split(" ")[2]
opp_team = teamgamelog.TeamGameLog(find_team_by_abbreviation(most_recent_game.MATCHUP.split(" ")[2])["id"])
opp_team_data = opp_team.get_data_frames()[0]
opp_team_game = opp_team_data.loc[opp_team_data["GAME_DATE"] == game_date].iloc[0]
nuggets_players_score = boxscores.get_data_frames()[0].loc[boxscores.get_data_frames()[0]["teamTricode"] == "DEN"]
fantasyPointsArr = [{"name":"Jokic", "fantasyPoints":0}, {"name":"Jokic", "fantasyPoints":0}, {"name":"Jokic", "fantasyPoints":0}]
for index, row in nuggets_players_score.iterrows():
    fantasyPoints = 0
    fantasyPoints += row["points"]
    fantasyPoints += row["assists"] * 1.5
    fantasyPoints += row["reboundsTotal"] * 1.2
    fantasyPoints += row["blocks"] * 3
    fantasyPoints += row["steals"] * 3
    fantasyPoints += row["turnovers"] * -1
    if fantasyPoints > min(fantasyPointsArr, key=lambda i: i["fantasyPoints"]).get("fantasyPoints"):
        fantasyPointsArr[fantasyPointsArr.index(min(fantasyPointsArr, key=lambda i: i["fantasyPoints"]))] = {"name":f"{row["firstName"]} {row["familyName"]}", "fantasyPoints":fantasyPoints, "points":row["points"], "assists":row["assists"], "rebounds":row["reboundsTotal"]}
        

pt_dif_percent = str(round((most_recent_game.PTS / previous_stats["avg_pts_past_10"])*100 - 100)) + "%"
fg_dif_percent = str(round(((most_recent_game.FG_PCT * 100) / previous_stats["avg_fg_past_10"]) * 100 - 100)) + "%"

if most_recent_game.PTS > opp_team_game.PTS:
    recent_game = f"NUGGETS WON!!!!!!!\nGame Date: {most_recent_game.GAME_DATE}\nScore: DEN {most_recent_game.PTS} - {opp_team_abb} {opp_team_game.PTS}\nDEN FG%: {str(float(round(most_recent_game.FG_PCT * 100, 2)))}, DEN 3PT%: {str(float(round(most_recent_game.FG3_PCT * 100, 2)))}\nPTS {pt_dif_percent} from 10 game average\nFG PCT {fg_dif_percent} from 10 game average\n<b>Best Performers</b>:\n1. {fantasyPointsArr[0].get("name")}\nPTS: {fantasyPointsArr[0].get("points")}, AST: {fantasyPointsArr[0].get("assists")}, REB: {fantasyPointsArr[0].get("rebounds")}\n2. {fantasyPointsArr[1].get("name")}\nPTS: {fantasyPointsArr[1].get("points")}, AST: {fantasyPointsArr[1].get("assists")}, REB: {fantasyPointsArr[1].get("rebounds")}\n3. {fantasyPointsArr[2].get("name")}\nPTS: {fantasyPointsArr[2].get("points")}, AST: {fantasyPointsArr[2].get("assists")}, REB: {fantasyPointsArr[2].get("rebounds")}"
else:
    recent_game = f"Game Date: {most_recent_game.GAME_DATE}\nScore: DEN {most_recent_game.PTS} - {opp_team_abb} {opp_team_game.PTS}\nDEN FG%: {str(float(round(most_recent_game.FG_PCT * 100, 2)))}, DEN 3PT%: {str(float(round(most_recent_game.FG3_PCT * 100, 2)))}\nPTS {pt_dif_percent} from 10 game average\nFG PCT {fg_dif_percent} from 10 game average\n<b>Best Performers</b>:\n1. {fantasyPointsArr[0].get("name")}\nPTS: {fantasyPointsArr[0].get("points")}, AST: {fantasyPointsArr[0].get("assists")}, REB: {fantasyPointsArr[0].get("rebounds")}\n2. {fantasyPointsArr[1].get("name")}\nPTS: {fantasyPointsArr[1].get("points")}, AST: {fantasyPointsArr[1].get("assists")}, REB: {fantasyPointsArr[1].get("rebounds")}\n3. {fantasyPointsArr[2].get("name")}\nPTS: {fantasyPointsArr[2].get("points")}, AST: {fantasyPointsArr[2].get("assists")}, REB: {fantasyPointsArr[2].get("rebounds")}"
print(recent_game)

TOKEN = "8063424590:AAHR7UKRB6egS0NmScYCMzzyf9oXVysv1wo"
CHAT_ID = "7164318863"
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={recent_game}&parse_mode=HTML"
print(requests.get(url).json())
