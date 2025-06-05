# create_dummy_population.py
import pandas as pd
import os

population = pd.DataFrame({
    "lat": [38.674, 38.676, 38.672],
    "lon": [39.222, 39.225, 39.227],
    "population_density": [8000, 12000, 5000]
})

os.makedirs("data/raw", exist_ok=True)
population.to_csv("data/raw/population.csv", index=False)

print(" population.csv created successfully.")
