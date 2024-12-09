import pandas as pd

# sort the df based on end_date
df = pd.read_json('UK_jobs/UK_job_applications.json')

df['end_date_2'] = pd.to_datetime(df['end_date'], format='%d-%b-%Y')
df = df.sort_values(by=['applied', 'end_date_2'])
df.drop('end_date_2', inplace=True, axis=1)

df.to_json("UK_jobs/UK_job_applications.json", orient='records', indent=2)

print("Data saved to the JSON.")
