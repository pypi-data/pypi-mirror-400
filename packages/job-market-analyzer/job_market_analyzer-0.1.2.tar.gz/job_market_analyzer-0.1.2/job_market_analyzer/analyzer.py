import pandas as pd
from importlib.resources import files, as_file


def load_jobs():
    resource = files("job_market_analyzer").joinpath("data/jobs.csv")
    with as_file(resource) as csv_path:
        return pd.read_csv(csv_path)



def filter_jobs(df, role):
    """Filter jobs by role"""                                  #Result:👉Only Data Analyst #jobsdf["job_title"] → column,#.str.contains() → text search
                                                                         #case=False → ignore case,#na=False → avoid errors
    return df[df["job_title"].str.contains(role, case=False, na=False)]


def top_skills(df):
    """Return most common skills"""
    skills_series = df["skills"].str.split(",").explode()    # Step-by-step:"SQL,Python,Excel" → split into list
    # explode() → convert list into rows,# #value_counts() → count frequency
    return skills_series.value_counts()


def salary_stats(df):
    """Return salary statistics"""
    return {
        "average_salary": int(df["salary"].mean()),
        "max_salary": int(df["salary"].max()),         #mean()=average
        "min_salary": int(df["salary"].min()),
    }


