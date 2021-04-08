
import numpy as np
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt

class Clustering:
    @staticmethod
    def compute_cluster(
            d:np.ndarray,
            ncluster:int,
            apply_scaling:bool=True,
            random_seed=None,
            n_iter=int(5e3),
            max_iter=int(1e5)
    ):
        if d.shape[0] == 0: return np.empty(0)
        if ncluster < 2: return np.empty(0)

        if apply_scaling: d = (d - d.mean(axis=0)) / d.std(axis=0)

        model = KMeans(n_clusters=ncluster,
                       n_init=n_iter,
                       max_iter=max_iter,
                       random_state=random_seed,
                       verbose=0).fit(d)
        clusters = model.predict(d)

        return clusters

    @staticmethod
    def plot_dendrogram(
            d:np.ndarray,
            apply_scaling:bool=True,
            nlevel=5,
            figsize=(10,6)
    ):
        if d.shape[0]==0: return None

        if apply_scaling: d = (d - d.mean(axis=0)) / d.std(axis=0)

        model = AgglomerativeClustering(distance_threshold=0,
                                        n_clusters=None).fit(d)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)
        Clustering.__plot_dendrogram__(model, truncate_mode='level', p=nlevel, ax=ax)



    @staticmethod
    def __plot_dendrogram__(model, **kwargs):
        # Create linkage matrix and then plot the dendrogram

        # create the counts of samples under each node
        counts = np.zeros(model.children_.shape[0])
        n_samples = len(model.labels_)
        for i, merge in enumerate(model.children_):
            current_count = 0
            for child_idx in merge:
                if child_idx < n_samples:
                    current_count += 1  # leaf node
                else:
                    current_count += counts[child_idx - n_samples]
            counts[i] = current_count

        linkage_matrix = np.column_stack([model.children_, model.distances_,
                                          counts]).astype(float)

        # Plot the corresponding dendrogram
        dendrogram(linkage_matrix, **kwargs)
