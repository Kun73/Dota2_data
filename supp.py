# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 15:17:36 2020

@author: huang kun
"""

import requests
import json
import pandas as pd
import numpy as np


def team_heros(team_id, ver_time):
    """Summary heros a team uses after a specific version

    Args:
        team_id: team id of a Dota2 team, can get from https://www.opendota.com/
        ver_time: Unix timestamp when the patch is released, convert from https://www.unixtimestamp.com/

    Returns:
        Two DataFrames containing heros and their ban/pick totals
    """
    r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(team_id))
    match = json.loads(r.text)
    match_id = []
    for m in match:
        if m['start_time'] > ver_time:  # Unix timestamp
            match_id.append(m['match_id'])
    heros = json.loads(requests.get('https://api.opendota.com/api/heroes').text)
    for hero in heros:
        hero.update({'pick_total': 0,
                     'ban_total': 0})
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
    return [own.T, against.T, len(match_id)]


# m = team_heros(15, 1574812800)
# VG:726228
def team_match_summary(team_id, ver_time):
    """summary match details of the team from ver_time

    Args:
        team_id: team id of a Dota2 team, can get from https://www.opendota.com/
        ver_time: Unix timestamp when the patch is released, convert from https://www.unixtimestamp.com/

    Returns:
        A DataFrame [against, league, teamfight_total, gold_adv_10, xp_adv_10, win]

    """
    r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(team_id))
    match = json.loads(r.text)
    match_id = []
    for m in match:
        if m['start_time'] > ver_time:  # Unix timestamp
            match_id.append(m['match_id'])
    match_summary = []
    for mid in match_id:
        match_data = json.loads(requests.get('https://api.opendota.com/api/matches/{}'.format(mid)).text)
        # get the position of team_id
        # pos = 1: dire, pos = 0: radiant
        temp = {}
        if match_data['dire_team']['team_id'] == team_id:
            pos = 1
            temp['against'] = match_data['radiant_team']['name']
        else:
            pos = 0
            temp['against'] = match_data['dire_team']['name']
        temp['league'] = match_data['league']['name']
        if match_data['teamfights'] is not None:
            temp['teamfight_total'] = len(match_data['teamfights'])
            if pos == 0:
                temp['gold_adv_10'] = match_data['radiant_gold_adv'][10]
                temp['xp_adv_10'] = match_data['radiant_xp_adv'][10]
                temp['win'] = match_data['radiant_win']
            else:
                temp['gold_adv_10'] = -match_data['radiant_gold_adv'][10]
                temp['xp_adv_10'] = -match_data['radiant_xp_adv'][10]
                temp['win'] = not (match_data['radiant_win'])
        else:
            temp['teamfight_total'] = None
            temp['gold_adv_10'] = None
            temp['xp_adv_10'] = None
            temp['win'] = None
        match_summary.append(temp)
    summary = pd.DataFrame(match_summary)
    return summary


# t = team_match_summary(726228, 1574812800)
def team_pick_winrate(team_id, ver_time):
    """summary match details of the team from ver_time

    Args:
        team_id: team id of a Dota2 team, can get from https://www.opendota.com/
        ver_time: Unix timestamp when the patch is released, convert from https://www.unixtimestamp.com/

    Returns:
        A dict containing
        winrates among heros, -1: this combination does not appear
        heros_all: original nested dict
    """
    r = requests.get('https://api.opendota.com/api/teams/{}/matches'.format(team_id))
    match = json.loads(r.text)
    match_id = []
    for m in match:
        if m['start_time'] > ver_time:  # Unix timestamp
            match_id.append(m['match_id'])
    heros1 = json.loads(requests.get('https://api.opendota.com/api/heroes').text)
    heros2 = json.loads(requests.get('https://api.opendota.com/api/heroes').text)  # avoid referring in dict

    for i in range(len(heros1)):
        del heros1[i]['name'], heros1[i]['primary_attr'], heros1[i]['attack_type'], heros1[i]['legs']
        del heros2[i]['name'], heros2[i]['primary_attr'], heros2[i]['attack_type'], heros2[i]['legs'], heros2[i][
            'roles']
        heros2[i].update({'pick_total': 0, 'win_total': 0, 'loss_total': 0})

    heros_all = {}
    heros_comb = {}
    for i in range(len(heros1)):
        heros_all[heros1[i]['id']] = heros1[i].copy()
        heros_comb[heros2[i]['id']] = heros2[i].copy()
        heros_all[heros1[i]['id']]['with'] = {}

    for hero_id in heros_all:
        for key, value in heros_comb.items():
            heros_all[hero_id]['with'][key] = value.copy()

    match_datas = []
    for mid in match_id:
        match_datas.append(json.loads(requests.get('https://api.opendota.com/api/matches/{}'.format(mid)).text))

    for hero_id in heros_all:
        for match_data in match_datas:
            # get the position of team_id
            # pos = 1: dire, pos = 0: radiant
            win = True
            if match_data['dire_team']['team_id'] == team_id:
                pos = 1
                win = not (match_data['radiant_win'])
            else:
                pos = 0
                win = match_data['radiant_win']

            # bp: 22 list, containing bp data
            bp = match_data['picks_bans']
            for s in bp:
                flag = False
                if s['hero_id'] == hero_id and s['team'] == pos and s['is_pick']:
                    flag = True
                    team_pick_hero_id = []
                    for s2 in bp:
                        if s2['team'] == pos and s2['is_pick']:
                            team_pick_hero_id.append(s2['hero_id'])
                    for hero_id_pick in team_pick_hero_id:
                        heros_all[hero_id]['with'][hero_id_pick]['pick_total'] += 1
                        if win:
                            heros_all[hero_id]['with'][hero_id_pick]['win_total'] += 1
                        else:
                            heros_all[hero_id]['with'][hero_id_pick]['loss_total'] += 1
                if flag:
                    break

    heros_name = []
    heros_id = []
    for hero in heros1:
        heros_name.append(hero['localized_name'])
        heros_id.append(hero['id'])
    winrate_table = pd.DataFrame(-1 * np.ones([len(heros_name), len(heros_name)]), columns=heros_name, index=heros_id)

    for h_id in heros_all:
        for hh_id in heros_all[h_id]['with']:
            if heros_all[h_id]['with'][hh_id]['pick_total'] != 0:
                winrate = heros_all[h_id]['with'][hh_id]['win_total'] / heros_all[h_id]['with'][hh_id]['pick_total']
                hero1_name = heros_all[h_id]['localized_name']
                hero2_id = heros_all[h_id]['with'][hh_id]['id']
                winrate_table[hero1_name][hero2_id] = winrate

    winrate_table.index = heros_name

    return {'winrate_table': winrate_table, 'heros_all': heros_all}
