# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 15:17:36 2020

@author: huang kun
"""

import requests
import json
import pandas as pd

def team_heros(team_id, ver_time):
    """Summary heros a team uses after a specific version
    
    Args:
        team_id: team id of a Dota2 team, can get from https://www.opendota.com/
        ver_time: Unix timestamp when the patch is released, convert from https://www.unixtimestamp.com/
    
    Returns:
        A DataFrame containing heros and their ban/pick totals
    """
    r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(team_id))
    match = json.loads(r.text)
    match_id = []
    for m in match:
        if m['start_time'] > ver_time: # Unix timestamp, after 7.23
            match_id.append(m['match_id'])
    heros = json.loads(requests.get('https://api.opendota.com/api/heroes').text)
    for hero in heros:
        hero.update({'pick_total':0,
                     'ban_total':0})
    heros_own = {}
    heros_against = {}
    for i in range(len(heros)):
        heros_own[heros[i]['id']] = heros[i].copy()
        heros_against[heros[i]['id']] = heros[i].copy()

    for mid in match_id:
        match_data = json.loads(requests.get('https://api.opendota.com/api/matches/{}'.format(mid)).text) 
        # get the position of team_id
        # pos = 1: dire, pos = 0: radiant
        if match_data['dire_team']['team_id'] == team_id:
            pos = 1
        else:
            pos = 0
        # bp: 22 list, containing bp data
        bp = match_data['picks_bans']
        for s in bp:
            if s['team'] == pos:
                if s['is_pick']:
                    heros_own[s['hero_id']]['pick_total'] += 1
                else:
                    heros_own[s['hero_id']]['ban_total'] += 1
            else:
                if s['is_pick']:
                    heros_against[s['hero_id']]['pick_total'] += 1
                else:
                    heros_against[s['hero_id']]['ban_total'] += 1
    own = pd.DataFrame(heros_own)
    against = pd.DataFrame(heros_against)
    return [own.T, against.T]

#m = team_heros(15, 1574812800)
