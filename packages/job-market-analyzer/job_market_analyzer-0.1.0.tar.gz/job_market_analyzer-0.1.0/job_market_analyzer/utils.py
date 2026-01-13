def save_to_csv(df, filename):       #Why utils? Reusable helpers Clean separation of logic
    df.to_csv(filename, index=False)
