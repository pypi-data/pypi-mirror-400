import matplotlib.pyplot as plt      #Matplotlib = base plotting library.


def plot_top_skills(skills_count):
    skills_count.head(5).plot(kind="bar")
    plt.title("Top Required Skills")
    plt.xlabel("Skills")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()



