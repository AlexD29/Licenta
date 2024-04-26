import pandas as pd

# Read the original train.csv file
df_train_original = pd.read_csv(r"../data/test.csv", encoding='utf-8')

# Drop columns B and C
df_train_modified = df_train_original.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'])

df_train_modified = df_train_modified.rename(columns={df_train_modified.columns[0]: 'Index'})
df_train_modified = df_train_modified.rename(columns={'Tweet': 'Content'})

# Save the modified DataFrame to a new CSV file with UTF-8 encoding
df_train_modified.to_csv(r"data/test_modified.csv", index=False, encoding='utf-8-sig')


