import numpy as np
import pandas as pd
import json
import geojson
import geopandas

# CONSTANTS
CATEGORIES = ['lawn', 'playground', 'bench', 'sports_courts', 'community_garden', 'water_fountain']

def call_to_server():  # TODO: call to server to get all json files for all plans in a project
    return plans_json_list

def get_data_from_json(plan_json):
    plan = json.loads(plan_json)  # TODO: how to read json file
    plan_id = plan['plan_id']
    geo_json = plan['geo_json_plan']
    geo_json_file_path = 'geo_json_temp.geojson'
    with open(geo_json_file_path, 'w') as geo_file:
        json.dumps(geo_json, geo_file)
    voters_table = plan['likes']
    no_votes = len(voters_table)
    return plan_id, geo_json_file_path, voters_table, no_votes

def get_data_from_geojson_geometry(x):
    ''' Read x: geometry field of geojson and output the area / length as feature'''
    geo_type = x.type
    feature = None
    if geo_type == 'Polygon':
        feature = x.area
    elif geo_type == 'LineString':
        feature = x.length
    elif geo_type == 'Point':
        feature = 1
    return feature

def compile_geo_features(plan_id, geo_json_file_path):
    df = geopandas.read_file(geo_json_file_path)
    features = df.geometry.apply(get_data_from_geojson_geometry)
    new_df = pd.concat([df.category, features], axis=1)
    new_df = new_df.groupby(['category']).sum().to_dict()
    output_dict = new_df['geometry']
    output_dict.update({'plan_id': int(plan_id)})
    return output_dict

def get_voter_stats(plan_id, voter_table):  # TODO: how will voter_table look like
    df = pd.DataFrame(voter_table)
    stats = dict({'plan_id': plan_id})
    stats['no_votes'] = len(df)
    stats['mean_no_children'] = df['no_children'].mean()
    stats['M_percent'] = sum(df['sex'] == 'M') / len(df)
    stats['F_percent'] = sum(df['sex'] == 'F') / len(df)
    age_groups = bin_ages(df['age'])
    stats.update(age_groups)
    return stats

def bin_ages(ages):
    bins = np.arange(0, 106, 15)
    binned_ages, bin_counts = np.unique(np.digitize(ages.values, bins, right=False), return_counts=True)
    age_groups = dict()
    for i, count in enumerate(bin_counts):
        age_groups[f"age_{bins[i]}-{bins[i+1]}"] = count / len(ages)
    return age_groups

def create_table_all_plans(plans_json_list):
    all_plans_df = pd.DataFrame(columns=['plan_id'] + CATEGORIES)
    vote_stats_df = pd.DataFrame()
    for plan in plans_json_list:
        plan_id, geo_json_file_path, voters_table, no_votes = get_data_from_json(plan)

        # geo features
        plan_dict = compile_geo_features(plan_id, geo_json_file_path)
        for n in no_votes:
            all_plans_df = all_plans_df.append(pd.Series(plan_dict), ignore_index=True)

        # voters stats
        vote_stats_dict = get_voter_stats(plan_id, voters_table)
        vote_stats_df = vote_stats_df.append(pd.Series(vote_stats_dict), ignore_index=True)

    return all_plans_df.fillna(0), vote_stats_df


""" json inpiut sample 
{
  "comments": [
    {
      "message": "Such a shitty plan", 
      "replies": [
        {
          "message": "You're an ass", 
          "userId": 4
        }
      ], 
      "userId": 2
    }
  ], 
  "geo_json_plan": "GEO JSON PLAN", 
  "is_official": false, 
  "likes": [
    1, 
    2
  ], 
  "userId": 1
}
"""