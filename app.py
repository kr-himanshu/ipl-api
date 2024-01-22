from flask import Flask, request
import ipl

app = Flask(__name__)

@ app.route('/')
def home():
    return "Welcome to IPL API"

@ app.route('/api/teams')
def teams():
    try:
        response = ipl.TeamAPI()
        return response
    except Exception as e:
        return f"Error in teams endpoint: {e}"

@ app.route('/api/players')
def players_list():
    try:
        response = ipl.PlayerAPI()
        return response
    except Exception as e:
        return f"Error in players_list endpoint: {e}"

@ app.route('/api/teamvsteam')
def teamvsteam():
    try:
        team1 = request.args.get('team1')
        team2 = request.args.get('team2')
        response = ipl.teamvsteam(team1, team2)
        return response
    except Exception as e:
        return f"Error in teamvsteam endpoint: {e}"

@ app.route('/api/team_record')
def team_record():
    try:
        team = request.args.get('team')
        response = ipl.TeamApi(team)
        return response
    except Exception as e:
        return f"Error in team_record endpoint: {e}"

@ app.route('/api/batting-record')
def batting_record():
    try:
        batsman = request.args.get('batsman')
        response = ipl.batsmanAPI(batsman)
        return response
    except Exception as e:
        return f"Error in batting_record endpoint: {e}"

@ app.route('/api/bowler_record')
def bowler_record():
    try:
        bowler = request.args.get('bowler')
        response = ipl.bowlerAPI(bowler)
        return response
    except Exception as e:
        return f"Error in bowler_record endpoint: {e}"

if __name__ == "__main__":
    app.run(debug=True)
