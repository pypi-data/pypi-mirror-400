import matplotlib.pyplot as plt            #Matplotlib = base plotting library.

def plot_top_skills(skills):
    skills.head(5).plot(kind="bar")
    plt.title("Top Skills Demand")
    plt.xlabel("Skills")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()   # 🔥 THIS IS THE KEY LINE

