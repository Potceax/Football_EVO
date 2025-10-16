import requests
import json
import time
import csv
import os
from dotenv import load_dotenv
from datetime import datetime


# Konfiguracja API
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': API_KEY
}

# ID Serie A w API-Football
SERIE_A_LEAGUE_ID = 135

# Zakres sezonów (ostatnie 3 lata)
current_year = datetime.now().year
SEASONS = [str(year) for year in range(current_year - 3, current_year)]

def get_fixtures_by_season(league_id, season):
    """Pobiera wszystkie mecze dla danego sezonu"""
    url = f"{BASE_URL}/fixtures"
    params = {
        'league': league_id,
        'season': season
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['response']:
            print(f"Pobrano {len(data['response'])} meczów dla sezonu {season}")
            return data['response']
        return []
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania meczów dla sezonu {season}: {e}")
        return []

def get_lineup_by_fixture(fixture_id):
    """Pobiera skład dla konkretnego meczu"""
    url = f"{BASE_URL}/fixtures/lineups"
    params = {
        'fixture': fixture_id
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data['response'] if data['response'] else None
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania składu dla meczu {fixture_id}: {e}")
        return None

def extract_players_from_lineup(lineup_data):
    """Wyciąga listę zawodników z danych składu"""
    players = []
    
    if not lineup_data:
        return players
    
    # Lineup_data zawiera składy obu drużyn
    for team_lineup in lineup_data:
        if 'startXI' in team_lineup:
            # Zawodnicy w podstawowym składzie
            for position_group in team_lineup['startXI']:
                player = position_group['player']
                players.append({
                    'id': player['id'],
                    'name': player['name']
                })
        
        if 'substitutes' in team_lineup:
            # Zawodnicy rezerwowi
            for substitute in team_lineup['substitutes']:
                player = substitute['player']
                players.append({
                    'id': player['id'],
                    'name': player['name']
                })
    
    return players

def save_to_csv(data, filename='serie_a_players.csv'):
    """Zapisuje dane do pliku CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['match_ID', 'player_ID', 'player_fullname']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        
        writer.writeheader()
        writer.writerows(data)
    
    print(f"\nDane zapisane do pliku: {filename}")

def Load(save_path):
    all_records = []
    total_fixtures = 0
    lineups_found = 0
    total_players = 0
    
    print("=== Pobieranie składów Serie A (ostatnie 3 sezony) ===\n")
    
    for season in SEASONS:
        print(f"\n--- Sezon {season}/{int(season)+1} ---")
        
        # Pobierz wszystkie mecze dla sezonu
        fixtures = get_fixtures_by_season(SERIE_A_LEAGUE_ID, season)
        total_fixtures += len(fixtures)
        
        for fixture in fixtures:
            fixture_id = fixture['fixture']['id']
            fixture_date = fixture['fixture']['date']
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            
            # Pobierz składy tylko dla zakończonych meczów
            if fixture['fixture']['status']['short'] in ['FT', 'AET', 'PEN']:
                print(f"Pobieranie składu: {home_team} vs {away_team} ({fixture_date})")
                
                lineup = get_lineup_by_fixture(fixture_id)
                
                if lineup:
                    lineups_found += 1
                    players = extract_players_from_lineup(lineup)
                    
                    # Utwórz rekord dla każdego zawodnika w meczu
                    for player in players:
                        record = {
                            'match_ID': fixture_id,
                            'player_ID': player['id'],
                            'player_fullname': player['name']
                        }
                        all_records.append(record)
                        total_players += 1
                
                # Opóźnienie aby nie przekroczyć limitu API
                time.sleep(1)
    
    # Zapisz do CSV
    if all_records:
        save_to_csv(all_records, save_path)
    
    print(f"\n=== Podsumowanie ===")
    print(f"Sprawdzonych meczów: {total_fixtures}")
    print(f"Meczów ze składami: {lineups_found}")
