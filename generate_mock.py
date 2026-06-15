import pandas as pd
import numpy as np
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
years_of_data = 10
draws_per_week = 2
weeks_per_year = 52

# The formula to calculate exactly how many rows to generate
total_draws = years_of_data * weeks_per_year * draws_per_week
# ==========================================

# Start from today's actual date
start_date = datetime.date.today()

data = []
# Start at the highest sequence number (the newest draw)
seq = total_draws

for i in range(total_draws):
    # Subtract days to walk BACKWARD in time for each previous draw
    # (7 days / draws_per_week gives us the exact day spacing)
    days_between_draws = 7 / draws_per_week
    draw_date = start_date - datetime.timedelta(days=(i * days_between_draws))
    
    # 6 picks from 1-37
    picks = np.random.choice(range(1, 38), size=6, replace=False)
    
    # 1 extra "strong" pick from 1-7
    strong_num = np.random.randint(1, 8) 
    
    data.append([
        seq, 
        draw_date.strftime("%Y-%m-%d"), 
        picks[0], picks[1], picks[2], picks[3], picks[4], picks[5],
        strong_num
    ])
    
    # Decrease sequence number as we go further back in time
    seq -= 1

df = pd.DataFrame(data, columns=['draw_seq', 'date', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'strong_num'])
df.to_csv('mock_historical_data.csv', index=False)

print(f"Successfully generated mock_historical_data.csv with {total_draws} total draws.")