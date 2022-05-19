"""Import scores from scores.txt and plot the scores"""
import matplotlib
import matplotlib.pyplot as plt
import math
import argparse
import os

# settings for matplotlib so we can export graphs to latex
matplotlib.use("pgf")
matplotlib.rcParams.update(
    {
        # Lualatex set as per https://tex.stackexchange.com/a/28833/177956
        "pgf.texsystem": "lualatex",
        "font.family": "serif",
        "text.usetex": True,
        "pgf.rcfonts": False,
    }
)


def weighted_avarage_last_100_scores(index, scores, weights):
    weighted_avarage = 0
    for i in range(100):
        weighted_avarage += weights[i] * scores[index - i]
    weighted_avarage /= sum(weights)
    return weighted_avarage


def calculate_avarages(scores):
    """Takes scores list and returns weighted avarages"""
    weights = [
        (math.sin(math.pi * (i / 100) - math.pi / 2) + 1) / 2 for i in range(1, 101)
    ]
    weights.reverse()
    avarages = []
    for i, score in enumerate(scores):
        if i < 100:
            avarages.append(sum(scores[: i + 1]) / len(scores[: i + 1]))
        else:
            avarages.append(weighted_avarage_last_100_scores(i, scores, weights))
    return avarages


def plot_scores(scores, avarages, destination):
    """Plots (game -> score) and avarages and saves the figure"""
    print(f"Saving graphs to directory: {destination}")
    max_score = max(scores)
    max_score_index = scores.index(max_score) + 1
    y = scores
    x = [i + 1 for i in range(len(y))]
    plt.rc("grid", linestyle="dotted")
    plt.scatter(x, y, color="black", marker=".", s=1)
    plt.scatter(
        max_score_index,
        max_score,
        color="red",
        marker=".",
        s=60,
        label=f"Max score",
    )
    plt.plot(x, avarages, color="blue", label="Weighted mean", linewidth=1)
    plt.xlabel("Game")
    plt.ylabel("Score")
    plt.grid(True)
    plt.legend()
    plt.savefig(destination + "scores.png", dpi=400)
    plt.savefig(destination + "scores.pgf")


def save_data_to_text_file(scores, scores_avarages, destination):
    """Saves (game -> score) array to text file"""
    max_score = max(scores)
    max_game_index = scores.index(max_score) + 1
    with open(destination + "scores.txt", "w", encoding="utf-8") as f:
        f.write(f"Max score: {max_score} at game: {max_game_index}\n")
        f.write(f"Avarage at the end: {scores_avarages[-1]}\n")
        f.write("Scores:\n")
        f.write(f"{scores}\n")
        f.write("Avarages:\n")
        f.write(f"{scores_avarages}")


def main():
    parser = argparse.ArgumentParser("plot_scores.py")
    parser.add_argument(
        "--source",
        type=str,
        default="data/scores.txt",
        help="source file to read scores from",
    )
    parser.add_argument(
        "--destination",
        type=str,
        default="data/",
        help="path of destination folder to write plotted graphs to",
    )
    arguments = parser.parse_args()
    source = arguments.source
    destination = arguments.destination
    if destination[-1] != "/":
        destination += "/"
    if not os.path.exists(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination))

    with open(source, "r", encoding="utf-8") as file:
        source_text = file.readlines()
    # fourth line is the scores in data/scores.txt
    scores = source_text[3]
    # slice off '[' and ']'
    scores = scores[1:-2]
    # create a list of strings of our scores
    scores = scores.split(", ")
    # convert to ints
    scores = [int(element) for element in scores]

    avarages = calculate_avarages(scores)
    plot_scores(scores, avarages, destination)
    save_data_to_text_file(scores, avarages, destination)


if __name__ == "__main__":
    main()
