import pandas as pd
import requests
import re
import logging
from crossfitgames.utils.transformation_functions import convert_object_columns_to_numeric, lb_to_kg, inch_to_cm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def games_json_dump(year=2022, division=1, page=1):
    """
    Fetches Crossfit Games leaderboard data from the API for a specific year, division, and page.

    Parameters:
        - year is from 2007 and to current
        - division is 1 for male, 2 for female and 0 for both
        - page is the leaderboard page you want, currently the max is 50 athletes per page.

    """
    logging.info(f"Starting API call for year {year}, division {division} and page {page}")

    if not isinstance(year, int):
        logging.error("Invalid type for 'year': Expected int")
        raise TypeError("year should be an integer")
    if not isinstance(division, int):
        logging.error("Invalid type for 'division': Expected int")
        raise TypeError("division should be an integer")
    if not isinstance(page, int):
        logging.error("Invalid type for 'page': Expected int")
        raise TypeError("page should be an integer")

    url = f"https://c3po.crossfit.com/api/leaderboards/v2/competitions/games/{year}/leaderboards?division={division}&sort=0&page={page}"
    logging.debug(f"Request URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"Successfully fetched data for year {year}, division {division} and page {page}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        raise

def games_info(year=2022, division=1):
    """
    Parses Crossfit Games leaderboard metadata for a specific year and division and returns a list of data.

    Parameters:
        - year is from 2007 and to current
        - division is 1 for male, 2 for female and 0 for both
    """
    logging.info(f"Fetching games info for year {year} and division {division}")
    
    response = games_json_dump(year=year, division=division)

    try:
        total_pages = response['pagination']['totalPages']
        total_competitors = response['pagination']['totalCompetitors']
        competition_id = response['competition']['competitionId']
        total_events = len(response['ordinals'])
        logging.info(f"Fetched games metadata: competition_id {competition_id}, total_pages {total_pages}, "
                     f"total_competitors {total_competitors} and total_events {total_events}")
    except KeyError as e:
        logging.error(f"Key missing in response: {e}")
        raise

    return [competition_id, total_pages, total_competitors, total_events]

def games_info_multiple(year_from=2018, year_too=2022, division=1):
    """
    Collects Crossfit Games leaderboard metadata for multiple years and returns that in a dataframe.

    Parameters:
        - year_xxx is from 2007 and to current
        - division is 1 for male, 2 for female and 0 for both
    """
    logging.info(f"Fetching multiple years games info from {year_from} to {year_too} for division {division}")

    df_games_info_multiple = pd.DataFrame(columns=['competitionId', 'totalPages', 'totalCompetitors', 'totalEvents', 'year', 'division'])

    division_value = [1] if division == 1 else [2] if division == 2 else [1, 2]
    for year in range(year_from, year_too + 1):
        try:
            for div in division_value:
                logging.info(f"Processing year {year} and division {div}")
                result_list = games_info(year, division=div)
                result_list.extend([year, div])
                temp_df = pd.DataFrame([result_list], columns=df_games_info_multiple.columns)
                df_games_info_multiple = pd.concat([df_games_info_multiple, temp_df], ignore_index=True)
        except Exception as e:
            logging.error(f"Error processing year {year} and division {div}: {e}")
            continue

    logging.info(f"Completed fetching games info from {year_from} to {year_too} for division {division}. Total records: {len(df_games_info_multiple)}")
    return convert_object_columns_to_numeric(df_games_info_multiple)

def games_info_competitors(year=2018, division=1):
    """
    Collects and processes competitor information for a specific Crossfit Games year and division and returns it in a dataframe.

    It uses the functions games_json_dump and games_info to get competitor information for 
    the specified Crossfit Games year and division returned as a Pandas dataframe.

    It also does some transformation on the data from the api. It uses the inch_to_cm and lb_to_kg functions
    to create two new columns and transforms age to integer.

    Parameters:
        - year is from 2007 and to current
        - division is 1 for male, 2 for female and 0 for both
    """
    logging.info(f"Fetching competitor info for year {year} and division {division}")

    df_games_info_competitors = pd.DataFrame()
    division_value = [1] if division == 1 else [2] if division == 2 else [1, 2]

    for div in division_value:
        try:
            logging.info(f"Processing division {div}")
            info_response = games_info(year=year, division=div)
            for page in range(1, info_response[1] + 1):
                try:
                    logging.info(f"Fetching page {page} for division {div}")
                    response = games_json_dump(year=year, division=div, page=page)
                    competitors_on_page = range(50) if page < info_response[1] else range(info_response[2] % 50)
                    for idx in competitors_on_page:
                        entrant_json = response['leaderboardRows'][idx]['entrant']
                        overallScore = response['leaderboardRows'][idx]['overallScore']
                        overallRank = response['leaderboardRows'][idx]['overallRank']
                        df_temp = pd.DataFrame([entrant_json])
                        df_temp['overallScore'] = overallScore
                        df_temp['overallRank'] = overallRank
                        df_games_info_competitors = pd.concat([df_games_info_competitors, df_temp], ignore_index=True)
                except Exception as e:
                    logging.error(f"Error processing page {page} for division {div}: {e}")
                    continue
        except Exception as e:
            logging.error(f"Error processing division {div}: {e}")
            continue

    # # Some transformations
    # clean lbs from weight
    df_games_info_competitors['weight'] = df_games_info_competitors['weight'].apply(lambda x: re.findall(r'\d+', x))
    # clean the "T" from workoutRank, this is when athletes are tied in a workout
    df_games_info_competitors['overallRank'] = df_games_info_competitors['overallRank'].apply(lambda x: re.findall(r'\d+', x))
    # change overallRank and overallScore to a numeric value so we can to some calculations
    df_games_info_competitors['overallRank'] = df_games_info_competitors['overallRank'].astype('int')
    df_games_info_competitors['age'] = df_games_info_competitors['age'].astype('int')
    # create a new columns and convert height to cm and weight to kg
    df_games_info_competitors = convert_object_columns_to_numeric(df_games_info_competitors)
    df_games_info_competitors['heightInCm'] = df_games_info_competitors['height'].apply(inch_to_cm)
    df_games_info_competitors['weightInKg'] = df_games_info_competitors['weight'].apply(lb_to_kg)

    logging.info(f"Fetched competitor info. Total competitors: {len(df_games_info_competitors)}")

    return df_games_info_competitors

def games_info_competitor_multiple(year_from=2018, year_too=2022, division=1):
         
    """
    This function uses the games_info_competitors function to get information on Crossfit Games competitors for multiple years returned as a Pandas dataframe.

    Parameters:
      - year_xxx is from 2007 and to last Games
      - division is 1 for male, 2 for female and 0 for both
    """   

    logging.info(f"Fetching competitors info from {year_from} to {year_too} for division {division}")    
    # create a dataframe to store info
    df_games_info_competitor_multiple = pd.DataFrame()
        
    # iterate over the selected years
    try:
      for year in range(year_from, year_too + 1):
          logging.info(f"Fetching competitors info {year} for division {division}")
          df_temp = games_info_competitors(year,division)
          df_temp['year'] = year
          df_games_info_competitor_multiple = pd.concat([df_games_info_competitor_multiple, df_temp], ignore_index=True)
    except KeyError as e:
      logging.error(f"Key missing in response: {e}")
      raise

    return(df_games_info_competitor_multiple)

def games_info_scores(year=2022, division=1):
    """
    This function uses the functions games_json_dump and games_info to get events score information for 
    the specified Crossfit Games year and division returned as a Pandas dataframe.

    Parameters:
        - year is from 2007 and to current
        - division is 1 for male, 2 for female and 0 for both
    """   
    # Initialize the dataframe to store scores
    df_games_info_scores = pd.DataFrame()

    # Determine division value
    if division == 1:
        division_value = [1]
    elif division == 2:
        division_value = [2]
    else:
        division_value = [1, 2]

    try:
        # Iterate over division_value
        for current_division in division_value:
            logging.info(f"Processing division {current_division} for year {year}.")
            
            # Collect games info
            info_response = games_info(year=year, division=current_division)
            total_pages, total_results = info_response[1], info_response[2]
            
            logging.info(f"Total pages: {total_pages}, Total results: {total_results}.")
            
            # Handle multiple pages
            for page in range(1, total_pages + 1):
                logging.info(f"Fetching data for page {page}.")
                
                # Fetch JSON data
                response = games_json_dump(year=year, division=current_division, page=page)
                
                if page == total_pages:  # Handle the last page
                    num_results = total_results - (total_pages - 1) * 50
                else:
                    num_results = 50
                
                for competitor_idx in range(num_results):
                    try:
                        scores_json = response['leaderboardRows'][competitor_idx]['scores']
                        df_temp = pd.json_normalize(scores_json)
                        df_temp['competitorId'] = response['leaderboardRows'][competitor_idx]['entrant']['competitorId']
                        df_temp['year'] = year
                        df_temp['division'] = current_division
                        df_games_info_scores = pd.concat([df_games_info_scores, df_temp], ignore_index=True)
                    except Exception as e:
                        logging.error(f"Error processing competitor index {competitor_idx}: {e}")
                        continue
            
        # Transform rank column and process numerical data
        logging.info("Transforming rank and other columns.")
        df_games_info_scores.loc[df_games_info_scores['rank'] == 'CUT', 'rankReason'] = 'CUT'
        df_games_info_scores.loc[df_games_info_scores['rank'] == 'WD', 'rankReason'] = 'WD'
        df_games_info_scores.loc[df_games_info_scores['rank'] == 'DNF', 'rankReason'] = 'DNF'
        df_games_info_scores.loc[df_games_info_scores['rank'].isin(['CUT', 'WD', 'DNF']), 'rank'] = 0
        df_games_info_scores = convert_object_columns_to_numeric(df_games_info_scores)
        df_games_info_scores['scoreIsWeightInKg'] = df_games_info_scores['scoreDisplay'].apply(lb_to_kg)
        
        logging.info("Dataframe transformation complete. Returning dataframe.")
        return df_games_info_scores
    
    except Exception as e:
        logging.critical(f"Error occurred in games_info_scores: {e}", exc_info=True)
        return pd.DataFrame()  # Return an empty dataframe as a fallback

def games_info_scores_multiple(year_from=2021, year_too=2022, division=1):
             
    """

        This function uses the games_info_scores function to get information on Crossfit Games 
        scores for multiple years returned as a Pandas dataframe.

        Parameters:
            - year is from 2007 and to current
            - division is 1 for male, 2 for female and 0 for both

    """   

    # error handling for function parameters
    if not isinstance(year_from, int):
        raise TypeError("year_from should be an integer")
    # error handling for function parameters
    if not isinstance(year_too, int):
        raise TypeError("year_too should be an integer")
    if not isinstance(division, int):
        raise TypeError("division should be an integer")
            
    # create a dataframe to store info
    df_games_info_scores_multiple = pd.DataFrame()
        
    # iterate over the selected years
    for year in range(year_from, year_too + 1):
        try:
          logging.info(f"Fetching games info score for year {year}")
          df_temp = games_info_scores(year,division)
          df_temp['year'] = year
          df_games_info_scores_multiple = pd.concat([df_games_info_scores_multiple, df_temp], ignore_index=True)
        except Exception as e:
            logging.error(f"Error processing games info scores for year {year} and division {div}")
            continue

    return(df_games_info_scores_multiple)