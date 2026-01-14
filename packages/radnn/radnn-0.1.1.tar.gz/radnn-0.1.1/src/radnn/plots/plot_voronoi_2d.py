# ======================================================================================
#
#     Rapid Deep Neural Networks
#
#     Licensed under the MIT License
# ______________________________________________________________________________________
# ......................................................................................

# Copyright (c) 2023-2025 Pantelis I. Kaplanoglou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# .......................................................................................
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

class PlotVoronoi2D(object):
  # --------------------------------------------------------------------------------------
  # Constructor
  def __init__(self, samples_2d, labels, ground_truth_cluster_count=10, title="2D Voronoi Plot"):
    # ................................................................
    # // Fields \\
    self.title                    = title
    self.samples_2d               = samples_2d
    self.labels                   = labels
    self.ground_truth_cluster_count  = ground_truth_cluster_count

    if (self.ground_truth_cluster_count <= 10):
      self.color_map   = cm.get_cmap("tab10")
    elif (self.ground_truth_cluster_count <= 20):
      self.color_map   = cm.get_cmap("tab20")
    else:
      self.color_map = cm.get_cmap("prism")

    self.point_size = 8
    self.plot_dimensions = [14, 8]
    # ................................................................
  # --------------------------------------------------------------------------------------
  def prepare_for_kmeans(self, kmeans_model):
    reduced_data = self.samples_2d

    # Step size of the mesh. Decrease to increase the quality of the VQ.
    #h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].
    h = .4     # point in the mesh [x_min, x_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
    y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans_model.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1, figsize=self.plot_dimensions)
    plt.clf()
    plt.imshow(Z, interpolation="nearest",
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=cm.get_cmap("tab20"), aspect="auto", origin="lower")

    #plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=self.labels, s=self.point_size, cmap=self.color_map)

    # Plot the centroids as a white X
    centroids = kmeans_model.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1], marker="x", s=169, linewidths=3
                ,color="w", zorder=10 )
    plt.title(self.title)
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
  # --------------------------------------------------------------------------------------
  def save(self, filename):
    plt.savefig(filename, bbox_inches='tight')
    return self
  # --------------------------------------------------------------------------------------
  def show(self):
    plt.show()
  # --------------------------------------------------------------------------------------