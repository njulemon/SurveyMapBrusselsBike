import shapefile
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd


def main():

    # read survey results
    data = pd.read_csv("Data/Survey/results_survey.csv")

    # rename columns
    data.columns = ['timestamp', 'score', 'postal_code']

    # Split municipality -> (postal_code, municipality_name)
    data["municipality"] = data["postal_code"].apply(lambda x: x[5:])
    data["postal_code"] = data["postal_code"].apply(lambda x: x[:4])

    mean_score = data.groupby("municipality").mean()
    print(mean_score)

    # read the map file
    sf = shapefile.Reader("Data/Map/UrbAdm_MUNICIPALITY")
    shapes = sf.shapes()
    records = sf.records()
    patches = []
    colors = []

    min_x = 1_000_000_000_000
    min_y = 1_000_000_000_000
    max_x = - 1_000_000_000_000
    max_y = - 1_000_000_000_000

    for i in range(len(shapes)):

        min_x = np.min([min_x, np.min([item[0] for item in sf.shape(i).points])])
        min_y = np.min([min_y, np.min([item[1] for item in sf.shape(i).points])])
        max_x = np.max([max_x, np.max([item[0] for item in sf.shape(i).points])])
        max_y = np.max([max_y, np.max([item[1] for item in sf.shape(i).points])])

        if records[i][2] in mean_score.index:
            polygon = Polygon(np.array(sf.shape(i).points), True)
            color = mean_score.loc[records[i][2]][0]
            patches.append(polygon)
            colors.append(color)

    # False polygon to chnage the scale of the color bar.
    patches.append(Polygon(np.array([[142000, 178000],[142001, 178000], [142001, 178001]]), True))
    colors.append(0.0)
    patches.append(Polygon(np.array([[142000, 178000], [142001, 178000], [142001, 178001]]), True))
    colors.append(5.0)

    # plot.
    fig, ax = plt.subplots()
    p = PatchCollection(patches)
    p.set_array(np.array(colors))
    ax.add_collection(p)
    fig.colorbar(p, ax=ax)

    # change the area to plot.
    ax.set_xlim([min_x, max_x])
    ax.set_ylim([min_y, max_y])

    ax.text(
            0.05,
            1.0,
            "Sur une échelle de 0 (cools) à 5 (insupportables), \nlorsque vous vous déplacer à vélo, comment décririez-vous \nle comportement des automobilistes que vous croisez ?",
            transform=ax.transAxes,
            fontsize=9
    )

    plt.axis('off')

    fig.show()


if __name__ == "__main__":
    main()