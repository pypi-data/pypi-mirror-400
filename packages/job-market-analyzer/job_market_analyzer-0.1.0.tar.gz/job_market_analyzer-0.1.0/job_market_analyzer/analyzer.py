import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path)         #📌 What it does:Reads CSV ,Converts it into DataFrame

def filter_jobs(df, role):
    return df[df["job_title"].str.contains(role, case=False, na=False)] #Result:👉Only Data Analyst #jobsdf["job_title"] → column,#.str.contains() → text search
                                                                         #case=False → ignore case,#na=False → avoid errors

def top_skills(df):                                          #Step-by-step:"SQL,Python,Excel" → split into list
    skills_series = df["skills"].str.split(",").explode()             #explode() → convert list into rows,# #value_counts() → count frequency
    return skills_series.value_counts()


def salary_stats(df):
    return {
        "average_salary": int(df["salary"].mean()), #mean()=average
        "max_salary": int(df["salary"].max()),
        "min_salary": int(df["salary"].min())
    }

df = load_data("../data/jobs.csv")

