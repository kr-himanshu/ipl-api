import numpy as np
import pandas as pd
import ast
import json

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

# Load the data
try:
    matches = pd.read_csv("D:/DATA SCIENCE/campusx/resources/class/ipl_matches.csv")
    balls = pd.read_csv("D:/DATA SCIENCE/campusx/resources/class/ipl_ball.csv")
except FileNotFoundError as e:
    print(f"Error: {e}")
    # Handle file not found error

# Merge the dataframes
try:
    data = matches.merge(balls, how='inner', on='ID')
    data['BowlingTeam'] = np.where(data['Team1'] == data['BattingTeam'], data['Team2'], data['Team1'])
    batter_data = data[np.append(balls.columns.values, ['BowlingTeam', 'Player_of_Match'])]
except Exception as e:
    print(f"Error in data merging: {e}")
    # Handle other exceptions

# Define a function to get unique teams
def TeamAPI():
    try:
        team = set(matches.Team1.unique()) | set(matches.Team2.unique())
        return json.dumps(list(team))
    except Exception as e:
        print(f"Error in TeamAPI: {e}")
        # Handle other exceptions

# Define a function to get unique players
def PlayerAPI():
    try:
        team1_players = matches.Team1Players.apply(ast.literal_eval)
        team2_players = matches.Team2Players.apply(ast.literal_eval)
        all_players = team1_players + team2_players
        player_name = set(player for sublist in all_players for player in sublist)
        return json.dumps(list(player_name))
    except Exception as e:
        print(f"Error in PlayerAPI: {e}")
        # Handle other exceptions

# Define a function to get head-to-head match statistics between two teams
def teamvsteam(team1, team2):
    try:
        temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) |
                          ((matches['Team1'] == team2) & (matches['Team2'] == team1))]
        mp = temp_df.shape[0]
        won = temp_df[temp_df['WinningTeam'] == team1].shape[0]
        nr = temp_df[temp_df['WinningTeam'].isnull()].shape[0]
        lost = mp - won - nr
        response = {'matches played': mp,
                    'team1 won': won,
                    'loss': lost,
                    'Draw': nr
                    }
        return response
    except Exception as e:
        print(f"Error in teamvsteam: {e}")
        # Handle other exceptions

# Define a function to get team's overall and against specific teams statistics
def self_record(team):
    try:
        df = matches[(matches['Team1'] == team) | (matches['Team2'] == team)]
        mp = df.shape[0]
        won = df[df['WinningTeam'] == team].shape[0]
        nr = df[df['WinningTeam'].isnull()].shape[0]
        lost = mp - won - nr
        nt = df[(df['WinningTeam'] == team) & (df['MatchNumber'] == 'Final')].shape[0]
        return {'matches played': mp,
                'won': won,
                'loss': lost,
                'Draw': nr,
                'title': nt}
    except Exception as e:
        print(f"Error in self_record: {e}")
        # Handle other exceptions

# Define a function to get team's overall and against specific teams statistics in JSON format
def TeamApi(team):
    try:
        self = self_record(team)
        Team = matches.Team1.unique()
        Team = [teams for teams in Team if teams != team]
        against = {team2: teamvsteam(team, team2) for team2 in Team}
        data = {'Overall': self, 'against': against}
        return json.dumps(data)
    except Exception as e:
        print(f"Error in TeamApi: {e}")
        # Handle other exceptions

# Define a function to get individual batter statistics
def batsmanRecord(batsman, df=batter_data):
    try:
        out = df[df.player_out == batsman].shape[0]
        df = df[df['batter'] == batsman]
        inngs = df.ID.unique().shape[0]
        runs = df.batsman_run.sum()
        fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
        sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
        if out:
            avg = round(runs / out)
        else:
            avg = np.inf
        nballs = df[~(df.extra_type == 'wides')].shape[0]
        if nballs:
            strike_rate = runs / nballs * 100
        else:
            strike_rate = 0
        gb = df.groupby('ID').sum()
        fifties = gb[(gb.batsman_run >= 50) & (gb.batsman_run < 100)].shape[0]
        hundreds = gb[gb.batsman_run >= 100].shape[0]
        try:
            highest_score = gb.batsman_run.sort_values(ascending=False).head(1).values[0]
            hsindex = gb.batsman_run.sort_values(ascending=False).head(1).index[0]
            if (df[df.ID == hsindex].player_out == batsman).any():
                highest_score = str(highest_score)
            else:
                highest_score = str(highest_score) + '*'
        except:
            highest_score = gb.batsman_run.max()
        not_out = inngs - out
        mom = df[df.Player_of_Match == batsman].drop_duplicates('ID', keep='first').shape[0]
        data = {
            'innings': inngs,
            'runs': runs,
            'fours': fours,
            'sixes': sixes,
            'avg': avg,
            'strikeRate': round(strike_rate),
            'fifties': fifties,
            'hundreds': hundreds,
            'highestScore': highest_score,
            'notOut': not_out,
            'mom': mom
        }
        return data
    except Exception as e:
        print(f"Error in batsmanRecord: {e}")
        # Handle other exceptions

# Define a function to get batter's statistics against specific teams
def batsmanVsTeam(batsman, team, df):
    try:
        df = df[df.BowlingTeam == team].copy()
        return batsmanRecord(batsman, df)
    except Exception as e:
        print(f"Error in batsmanVsTeam: {e}")
        # Handle other exceptions

# Define a function to get batter statistics in JSON format
def batsmanAPI(batsman, df=batter_data):
    try:
        df = df[df.innings.isin([1, 2])]  # Excluding Super overs
        self_record = batsmanRecord(batsman, df=df)
        TEAMS = matches.Team1.unique()
        against = {team: batsmanVsTeam(batsman, team, df) for team in TEAMS}
        data = {
            batsman: {'all': self_record,
                      'against': against}
        }
        return json.dumps(data, cls=NpEncoder)
    except Exception as e:
        print(f"Error in batsmanAPI: {e}")
        # Handle other exceptions

# Copy batter_data to create bowler_data
bowler_data = batter_data.copy()

# Define a function to preprocess bowler data and calculate runs and wickets for bowlers
def bowler_run(x):
    try:
        if x[0] in ['penalty', 'legbyes', 'byes']:
            return 0
        else:
            return x[1]
    except Exception as e:
        print(f"Error in bowler_run: {e}")
        # Handle other exceptions

# Apply the function to create a new column 'bowler_run'
bowler_data['bowler_run'] = bowler_data[['extra_type', 'total_run']].apply(bowler_run, axis=1)

# Define a function to preprocess bowler data and identify wickets for bowlers
def bowler_wicket(x):
    try:
        if x[0] in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']:
            return x[1]
        else:
            return 0
    except Exception as e:
        print(f"Error in bowler_wicket: {e}")
        # Handle other exceptions

# Apply the function to create a new column 'isbowlerwicket'
bowler_data['isbowlerwicket'] = bowler_data[['kind', 'isWicketDelivery']].apply(bowler_wicket, axis=1)

# ... (previous code)

# Define a function to get bowler statistics
def bowler_record(bowler, df=bowler_data):
    try:
        df = df[df['bowler'] == bowler]
        innings = df.ID.unique().shape[0]
        nballs = df[~(df.extra_type.isin(['wides', 'noballs']))].shape[0]
        runs = df['bowler_run'].sum()

        # Calculate economy rate
        if nballs:
            eco = runs / nballs * 6
            eco = round(eco, 2)
        else:
            eco = 0

        fours = df[(df.batsman_run == 4) & (df.non_boundary == 0)].shape[0]
        sixes = df[(df.batsman_run == 6) & (df.non_boundary == 0)].shape[0]
        wicket = df.isbowlerwicket.sum()

        # Calculate average
        if wicket:
            avg = runs / wicket
            avg = round(avg, 2)
        else:
            avg = np.inf

        # Calculate strike rate
        if wicket:
            strike_rate = nballs / wicket * 100
            strike_rate = round(strike_rate, 2)
        else:
            strike_rate = np.nan

        gb = df.groupby('ID').sum()
        w3 = gb[(gb.isbowlerwicket >= 3)].shape[0]

        # Find the best bowling figure
        best_wicket = gb.sort_values(['isbowlerwicket', 'bowler_run'], ascending=[False, True])[
            ['isbowlerwicket', 'bowler_run']].head(1).values

        if best_wicket.size > 0:
            best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
        else:
            best_figure = np.nan

        mom = df[df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]

        data = {
            'innings': innings,
            'wicket': wicket,
            'economy': eco,
            'average': avg,
            'avg': avg,
            'strikeRate': strike_rate,
            'fours': fours,
            'sixes': sixes,
            'best_figure': best_figure,
            '3+W': w3,
            'mom': mom
        }
        return data
    except Exception as e:
        print(f"Error in bowler_record: {e}")
        # Handle other exceptions

# Define a function to get bowler statistics against specific teams
def bowlerVsTeam(bowler, team, df):
    try:
        df = df[df.BattingTeam == team].copy()
        return bowler_record(bowler, df)
    except Exception as e:
        print(f"Error in bowlerVsTeam: {e}")


# Define a function to get bowler statistics in JSON format
def bowlerAPI(bowler, balls=bowler_data):
    try:
        df = balls[balls.innings.isin([1, 2])]  # Excluding Super overs
        self_record = bowler_record(bowler, df=df)
        TEAMS = matches.Team1.unique()
        against = {team: bowlerVsTeam(bowler, team, df) for team in TEAMS}
        data = {
            bowler: {'all': self_record,
                     'against': against}
        }
        return json.dumps(data, cls=NpEncoder)
    except Exception as e:
        print(f"Error in bowlerAPI: {e}")
