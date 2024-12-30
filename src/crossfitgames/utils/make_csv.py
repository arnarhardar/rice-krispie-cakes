import pandas as pd
from api_calls import *

def make_crossfitgames_csv()
df = games_info_competitor_multiple(2007,2022,0)
df.to_csv('../../data/games_info_competitor_2007_2022.csv')