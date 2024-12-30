from src.api.api_calls import games_info_multiple
import time
timestr = time.strftime("%Y%m%d_%H%M%S")
data = games_info_multiple()
data.to_csv(f"data/games_info_multiple_dump_{timestr}.csv")