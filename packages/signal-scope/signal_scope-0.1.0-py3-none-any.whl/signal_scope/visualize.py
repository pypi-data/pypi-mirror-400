import matplotlib.pyplot as plt


def plot_series(series, title="Signal Plot"):
    plt.figure(figsize=(8, 3))
    plt.plot(series.values, linewidth=1.5)
    plt.title(title)
    plt.tight_layout()
    plt.show()
