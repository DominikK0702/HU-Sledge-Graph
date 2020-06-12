import matplotlib.pyplot as plt


fig, axes = plt.subplots(2, sharey=True)
axes[0].plot([1, 2], [1, 2])
axes[1].plot([1, 2], [3, 4])
fig.show()
