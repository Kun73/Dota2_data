# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 15:17:36 2020

@author: huang kun
"""

import requests
import json

def team_heros(team_id, ver_time):
    """Summary heros a team uses after a specific version
    
    Args:
        team_id: team id of a Dota2 team, can get from https://www.opendota.com/
        ver_time: Unix timestamp when the patch is released, convert from https://www.unixtimestamp.com/
    
    Returns:
        A dict mapping keys to the corresponding table row data fetched.
        Each row is represented as a tuple of integer(wins, loses, winrate).
        For example:
        
        ['lich':(9, 1, 0.9),
         ...
        ]
    """
    r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(team_id))
    match = json.loads(r.text)
    match_id = []
    for m in match:
        if m['start_time'] > ver_time: # Unix timestamp, after 7.23
            match_id.append(m['match_id'])
    return match_id