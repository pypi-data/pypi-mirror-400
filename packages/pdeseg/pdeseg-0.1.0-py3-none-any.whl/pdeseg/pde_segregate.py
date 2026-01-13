import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from collections import defaultdict
from scipy.stats import gaussian_kde
from joblib import Parallel, delayed

class PDE_Segregate():
    def __init__(
            self, integration_method="trapz", delta=500,
            bw_method="scott", k=2, n_jobs=1,
            lower_end=-1.5, upper_end=2.5,
            averaging_method="mean", mode="release"
    ):
        """
        Parameters
        ----------
        integration_method : str
         - Integration method.

           Available options include 'numpy.trapz' (default) and 'sum'.

        delta : int
         - Number of cells in the x-grid

        bw_method : str, scalar or callable
         - The method used to calculate the estimator bandwith. This can be
           'scott' and 'silverman', a scalar constant or a callable. For
           more details, see scipy.stats.gaussian_kde documentation.

        k : intpairwise
         - Compute the mean intersection area between (number of classes)
           choose k combinations of intersection areas.

        n_jobs : int
         - Number of processors to use. -1 to use all available processors.

        lower_end : float
         - Lower end of the grid to evaluate the KDEs.

        upper_end : float
         - Upper end of the grid to evaluate the KDEs.

        averaging_method : str
         - Method of averaging the combinations of intersection areas.
           Available options include:
           1. "mean" : The mean of all the combinations of intersection areas
           2. "weighted" : A weighted mean of all the combinations of intersection areas

        mode : str ("release", "development")
         - Option implemented during development to return constructed kernels
           PDEs.
        """
        self.integration_method = integration_method
        self.delta = delta
        self.bw_method = bw_method
        self.k = k
        self.n_jobs = n_jobs
        self.mode = mode
        self.averaging_method = averaging_method

        # Initializing the x-axis grid
        if lower_end > 0.0:
            raise ValueError("Parameter lower_end must be less than 0.0!")
        else:
            self.leftEnd = lower_end

        if upper_end < 1.0:
            raise ValueError("Parameter upper_end must be greater than 1.0!")
        else:
            self.rightEnd = upper_end

    def fit(self, X, y):
        """
        Get the intersection areas of the PDE of class-segregated groups.

        Parameters
        ----------
        X : np.array
         - Dataset with the shape: (n_samples, n_features)

        y : np.array
         - Class vector
        """
        self.y = y

        # Min-max normalization of dataset
        X_sub = X - X.min(axis=0)
        self.X = X_sub / X_sub.max(axis=0)

        # Grouping the samples according to unique y label
        self.y_segregatedGroup, self.y_segregatedGroup_sd, self.y_segregatedGroup_mean = self.segregateX_y()

        # Initializing a list of available classes
        self.yLabels = list(self.y_segregatedGroup.keys())
        self.yLabels.sort()

        # Check to make sure user does not enter an invalid parameter 'n'
        if self.k > len(self.yLabels):
            raise ValueError(
                f"Parameter n must be between 2 and number of class ({len(self.yLabels)})!"
            )

        if self.k == 1:
            raise ValueError(
                f"Parameter n must be between 2 and number of class ({len(self.yLabels)})!"
            )

        # Initializing the default grid
        mid_grid= np.linspace(0.0, 1.0, int(self.delta))
        self.grid_width = mid_grid[1] - mid_grid[0]

        if self.leftEnd != 0.0:
            leftGrid = np.arange(self.leftEnd, 0.0, self.grid_width)
            self.XGrid = np.concatenate((leftGrid, mid_grid))
        else:
            self.XGrid = mid_grid

        if self.rightEnd != 1.0:
            rightGrid = np.arange(1.0, self.rightEnd, self.grid_width)
            self.XGrid = np.concatenate((self.XGrid, rightGrid))

        # Do not allow user to use PDE-Segregate, when class has only one sample
        yToRemove = []
        for y in self.y_segregatedGroup.keys():
            if self.y_segregatedGroup[y].shape[0] == 1:
                yToRemove.append(y)
                print(
                    f"---\ny={y} sub-dataset has only 1 sample and will be " +
                    "excluded ... "
                )
        #  - removing class populations with only one sample
        if len(yToRemove) != 0:
            for y in yToRemove:
                self.y_segregatedGroup.pop(y, None)
        #  - abort if all remaining samples belong to only one single class
        if len(self.y_segregatedGroup) == 1:
            raise ValueError(
                "There's only one target label, " +
                f"y={self.y_segregatedGroup.keys()}"
            )

        # Construct kernel density estimator per class for every feature
        print(
            "Constructing and evaluating the KDEs per class for every feature ... "
        )
        self.pdes = []
        self.grids = []

        delayed_calls = (
            delayed(
                self.construct_kernel
            )(feat_idx) for feat_idx in range(self.X.shape[1])
        )
        res = Parallel(n_jobs=self.n_jobs, verbose=0)(delayed_calls)
        if self.mode == "development":
            self.feature_kernels = []
            for item in res:
                self.feature_kernels.append(item[0])
                self.pdes.append(item[1])
                self.grids.append(item[2])
        elif self.mode == "release":
            for item in res:
                self.pdes.append(item[0])
                self.grids.append(item[1])

        print(" - Kernels constructed!")

        # Compute intersection areas
        _combinations = combinations(self.yLabels, self.k)
        c1 = []
        cStack = []
        print("Computing intersection areas ...")
        for c in _combinations:
            c1.append(c)
            delayed_calls_intersectionArea = (
                delayed(
                    self.compute_intersectionArea
                )(feat_idx, c) for feat_idx in range(self.X.shape[1])
            )
            c_intersection = Parallel(
                n_jobs=self.n_jobs, backend="threading", verbose=0
            )(delayed_calls_intersectionArea)

            cStack.append(c_intersection)

        cStack = np.array(cStack)

        if self.averaging_method == "mean":
            print(" - averaging_method: 'mean'")
            self.intersectionAreas = np.mean(cStack, axis=0)

        elif self.averaging_method == "weighted":
            print(" - averaging_method: 'weighted'")
            nSamples_total = self.X.shape[0]
            nSamples_perClass = defaultdict()
            for _class in self.y_segregatedGroup.keys():
                nSamples_perClass[_class] = self.y_segregatedGroup[_class].shape[0]

            _weights = np.zeros(len(c1))
            for _wi, _c in enumerate(c1):
                _weight = (
                    nSamples_perClass[_c[0]] + nSamples_perClass[_c[1]]
                ) / nSamples_total
                _weights[_wi] = _weight

            # Normalized such that the sum of all the weights are 1
            _norm_weights = _weights / _weights.sum()

            intAreas = np.zeros(self.X.shape[1])
            for _ci in range(len(c1)):
                intAreas += cStack[_ci,:] * _norm_weights[_ci]

            self.intersectionAreas = intAreas

        else:
            raise ValueError(
                "Acceptable options for the parameter 'averaging_method' are: " +
                "('mean', 'weighted')"
            )

        # Get feature importances as expressed in terms of reciprocal of
        # computed intersection areas
        self.feature_importances_ = 1/self.intersectionAreas

    def compute_intersectionArea(self, feat_idx, _combinations):
        """
        Compute intersection area between estimated PDEs.

        Parameters
        ----------
        feat_idx : int
         - Index of the desired feature in the given dataset, X.

        pairwise : tuple
         - Pair of indices indicating which pair of classes to compare.

        Returns
        -------
        OA : float
         - Computed intersection area of the PDEs.
        """
        yStack = []

        for c in _combinations:
            yStack.append(self.pdes[feat_idx][c])

        yIntersection = np.amin(yStack, axis=0)

        if self.integration_method == "sum":
            OA = (yIntersection.sum())/delta
        elif self.integration_method == "trapz":
            OA = np.trapz(yIntersection, self.grids[feat_idx])
        else:
            raise ValueError(
                "Possible options for <integration_method>: " +
                "('trapz', 'sum')"
            )

        return OA

    def construct_kernel(self, feat_idx):
        """
        Construct the kernel density estimator of all the class-segregated groups
        for a given feature.

        Parameters
        ----------
        feat_idx : int
         - Index of the desired feature in the given dataset, X.

        Returns
        -------
        pdes : dict
         - dict[class]: Evaluated KDEs along grid.

        _grid : np.array
         - Grid to evaluated KDE needed for trapezoidal integration.

        If self.mode=="development":
        kdes : dict
         - dict[class]: Constructed KDE.

        """
        kernels = defaultdict(); pdes = defaultdict()

        special_means = np.array(())

        # To account for cases where all samples in the population are
        # centered at the local mean
        for y in self.yLabels:
            if self.y_segregatedGroup_sd[y][feat_idx] <= 2*self.grid_width:
                # Fit mean into the grid
                special_means = np.append(
                    special_means, self.y_segregatedGroup_mean[y][feat_idx]
                )

        special_means = np.sort(special_means)

        if len(special_means) > 0:
            lefthalf  = np.where(self.XGrid < special_means[0])[0]
            righthalf = np.where(self.XGrid > special_means[-1])[0]

            _grid = self.XGrid[lefthalf]
            for _mean in special_means:
                _grid = np.append(_grid, _mean)
            _grid = np.concatenate((_grid, self.XGrid[righthalf]))

        else:
            _grid = self.XGrid

        for y in self.yLabels:
            kernel = gaussian_kde(
                self.y_segregatedGroup[y][:,feat_idx], self.bw_method
            )
            kernels[y] = kernel

            pde = np.reshape(kernel(_grid).T, len(_grid))
            pdes[y] = pde

        if self.mode == "development":
            return kernels, pdes, _grid
        elif self.mode == "release":
            return pdes, _grid

    def segregateX_y(self):
        """
        Routine to segregate X samples into unique y groups
        """
        unique_y = list(set(self.y))

        _subX = defaultdict()
        _subX_sd = defaultdict()
        _subX_mean = defaultdict()
        for uy in unique_y:
            _subX[uy] = self.X[np.where(self.y==uy)[0], :]

            # Add 'zero' to last element to allow for scipy to carry out
            # a Cholesky Decomposition on the variance matrix
            _subX[uy][-1] += 1e-15

            # Compute standard deviation per population per feature
            _subX_sd[uy] = _subX[uy].std(axis=0)

            # Compute mean per population per feature
            _subX_mean[uy] = _subX[uy].mean(axis=0)

        return _subX, _subX_sd, _subX_mean

    def get_topnFeatures(self, n):
        """
        Returns the indices of the top n features (smaller intersection areas
        are more important).

        Parameters
        ----------
        n : int
         - Desired number of top features

        Returns
        -------
        inds_topFeatures : list
         - List of top n features, starting from the most to least important
           features.
        """
        return sorted(
            range(len(self.intersectionAreas)),
            key=lambda i: self.intersectionAreas[i],
            reverse=False
        )[:n]

    def plot_overlapAreas(
            self, feat_idx, feat_names=None, _combinations=None,
            show_samples=False, legend=False, _ax=None
    ):
        """
        Function to plot intersection areas for a given feature.

        Parameters
        ----------
        feat_idx : int
         - Index of feature to plot according to input X.

        feat_names : list or None
         - List of feature names in order of features according to input X.
           If None, integer indices will be used.

        _combinations : tuple or None
         - Tuple of which classes to consider when plotting the
           intersection area. If None, then plots intersection area
           between all KDEs (k=number of class).

        show_samples : bool
         - If True, show samples that make up the KDEs as short vertical lines.

        legend : bool, 'intersection', 'class'
         - If true, legend would include all the class PDEs and computed
           intersection areas. If 'intersection', only includes
           intersection area, and 'class' only includes the classes

        _ax : matplotlib.axes.Axes
         - Matplotlib's Axes object, if None, one will be created internally.

        """
        if _ax is None:
            fig, _ax = plt.subplots(1,1)
            _ax_passed = False
        else:
            _ax_passed = True

        linecolors = []

        if _combinations is None:
            pdes_perFeature = self.pdes[feat_idx]
        else:
            pdes_perFeature = defaultdict()
            for y in _combinations:
                if not y in self.yLabels:
                    raise ValueError(
                        f"The class {y} was not found in the original class array y" +
                        f"\nTypes of classes: {self.yLabels}"
                    )
                else:
                    pdes_perFeature[y] = self.pdes[feat_idx][y]

        # Initialize yStack
        yStack = []
        for y, p_y in pdes_perFeature.items():
            yStack.append(p_y)

        # First plot all KDEs regardless of user input
        if isinstance(legend, str):
            if legend == "intersection":
                class_legendlabels = False
                area_legendlabel = True
                show_legend = True
            elif legend == "class":
                class_legendlabels = True
                area_legendlabel = False
                show_legend = True
            else:
                raise ValueError(
                    "Possible values for 'legend' are 'intersection', " +
                    "'class' or boolean"
                )
        else:
            if legend:
                class_legendlabels = True
                area_legendlabel = True
                show_legend = True
            else:
                class_legendlabels = False
                area_legendlabel = False
                show_legend = False

        for y, p_y in self.pdes[feat_idx].items():
            if class_legendlabels:
                p = _ax.plot(self.grids[feat_idx], p_y, alpha=0.7, label=f"Class {y}")
            else:
                p = _ax.plot(self.grids[feat_idx], p_y, alpha=0.7)

            # Get line colors
            linecolors.append(p[0].get_color())

        # Plotting the data samples
        if show_samples:
            yMax = _ax.get_ylim()[1]
            for i, k in enumerate(self.pdes[feat_idx].keys()):
                _ax.vlines(
                    self.y_segregatedGroup[k][feat_idx], 0.0, 0.03*yMax,
                    color=linecolors[i], alpha=0.7
                )

        # Getting the smallest probabilities of all the estimates at every
        # grid point
        yIntersection = np.amin(yStack, axis=0)

        # Get OA
        if _combinations is None:
            OA = self.compute_intersectionArea(feat_idx, self.yLabels)
        else:
            OA = self.compute_intersectionArea(feat_idx, _combinations)

        if show_legend:
            if area_legendlabel:
                if _combinations is None:
                    _label_underscript = 'd'
                else:
                    _label_underscript = str(_combinations)
                    _label_underscript = _label_underscript.replace(' ', '')

                _label = r"$A_{" + _label_underscript + r"}=$"
                _label += str(round(OA, 3))
                fill_poly = _ax.fill_between(
                    self.grids[feat_idx], 0, yIntersection, label=_label,
                    color="lightgray", edgecolor="lavender"
                )
            else:
                fill_poly = _ax.fill_between(
                    self.grids[feat_idx], 0, yIntersection,
                    color="lightgray", edgecolor="lavender"
                )
            _ax.legend()
        else:
            fill_poly = _ax.fill_between(
                self.grids[feat_idx], 0, yIntersection,
                color="lightgray", edgecolor="lavender"
            )

        fill_poly.set_hatch('xxx')

        if not feat_names is None:
            _ax.set_xlabel(feat_names[feat_idx], fontsize='large')
        else:
            _ax.set_xlabel(f"Feature {feat_idx}", fontsize='large')

        xrange = self.grids[feat_idx].max() - self.grids[feat_idx].min()
        _ax.set_xlim(
            (
                self.grids[feat_idx].min()-(xrange*0.05),
                self.grids[feat_idx].max()+(xrange*0.05)
            )
        )
        _ax.set_xticks(
            np.arange(
                self.grids[feat_idx].min()-(xrange*0.05),
                self.grids[feat_idx].max()+(xrange*0.05),
                0.5
            )
        )
