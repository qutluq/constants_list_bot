import pandas as pd
import numpy as np

constants_df   = pd.read_csv('.\\data\\constants.csv', skiprows=5)

print(constants_df.head())