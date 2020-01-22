import numpy as np
import pandas as pd
import geojson
import geopandas

# CONSTANTS
CATEGORIES = ['lawn', 'playground', 'bench', 'sports_courts', 'community_garden', 'water_fountain']

def get_data_from_geojson(x):
    geo_type = x.type
    feature = None
    if geo_type == 'Polygon':
        feature = x.area
    elif geo_type == 'LineString':
        feature = x.length
    elif geo_type == 'Point':
        feature = 1
    return feature

def compile_features(plan_id, geo_json):
    df = geopandas.read_file(geo_json)
    features = df.geometry.apply(get_data_from_geojson)
    new_df = pd.concat([df.category, features], axis=1)
    new_df = new_df.groupby(['category']).sum().to_dict()
    output_dict = new_df['geometry']
    output_dict.update({'plan_id': int(plan_id)})
    return output_dict

def create_table_all_plans(plans):
    all_plans_df = pd.DataFrame(columns=['plan_id'] + CATEGORIES)
    # read plans' geojsons
    for plan_id, geo_json in plans:
        plan_dict = compile_features(plan_id, geo_json)
        all_plans_df = all_plans_df.append(pd.Series(plan_dict), ignore_index=True)
    return all_plans_df.fillna(0)