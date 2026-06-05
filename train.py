import pandas as pd

df = pd.read_csv("dataset.csv")

print("Total Diseases:")
print(df["Disease"].nunique())

print("\nDisease Names:")
print(df["Disease"].unique())