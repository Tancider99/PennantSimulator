from save_manager import SaveManager
import pprint

if __name__ == '__main__':
    sm = SaveManager()
    data = sm.load_game(1)
    if not data:
        print('No save data loaded')
    else:
        teams = data.get('teams', [])
        if not teams:
            print('No teams in save')
        else:
            first_team = teams[0]
            players = first_team.get('players', [])
            if not players:
                print('No players in first team')
            else:
                p0 = players[0]
                print('First player (raw dict):')
                pprint.pprint(p0)
                stats = p0.get('stats', {})
                print('\nStats values:')
                pprint.pprint(stats)
