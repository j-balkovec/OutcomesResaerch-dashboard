# %%
import pandas as pd

file = "/Users/jbalkovec/Desktop/MSc/OutcomesResearch/rest_tableau.csv"

df = pd.read_csv(file)

print(df.columns)
