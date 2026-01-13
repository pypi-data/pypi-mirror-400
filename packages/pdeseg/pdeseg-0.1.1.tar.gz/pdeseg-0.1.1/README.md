<p align="center">
  <img src="https://github.com/RenZhen95/PDE-Segregate/blob/main/docs/artwork/logo.svg" width="300">
</p>

**PDE-Seg (PDE-Segregate)** is a univariate filter feature selection method based on a filter-measure that ranks features according to their ability to segregate the probability density estimates (PDE) of the class samples.

## Install
PDE-Seg can be installed from PyPI:
<pre>
pip install pdeseg
</pre>

## Example
```python
from pdeseg import PDE_Segregate

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification

# Create random classification dataset
X, y = make_classification(
    n_samples=300, n_features=50, n_classes=3, n_informative=5,
    shuffle=False
)

# Initialize PDE-Segregate object
pdeRanker = PDE_Segregate()

# Carry out feature selection
pdeRanker.fit(X, y)

# Get top 10 features
top10Features = pdeRanker.get_topnFeatures(10)

# Visualize the top feature's ability to segregate PDEs
fig, axs = plt.subplots(1, 2, sharey=True)

# Top ranked feature
pdeRanker.plot_overlapAreas(top10Features[0], legend="intersection", _ax=axs[0])
axs[0].set_title("Most relevant feature", loc="left")

# Last ranked feature
pdeRanker.plot_overlapAreas(49, legend="intersection", _ax=axs[1])
axs[1].set_title("Least relevant feature", loc="left")

axs[0].set_ylabel(r"Probability Density, $\hat{P}$")
for i in range(2):
    axs[i].set_xlim(-0.5, 1.5)
    axs[i].set_xticks(np.arange(-0.5, 2.0, 0.5))
```
<p align="center">
  <img src="https://github.com/RenZhen95/PDE-Segregate/blob/main/docs/artwork/example_plot.svg" width="550">
</p>

Check out the notebooks provided as tutorials and examples of some specific use cases.

## Citation
For now, cite the followinng abstract
> J.C. Liaw, F. Geu Flores. A novel univariate feature selection filter-measure based on the reduction of class overlapping. 94th Annual Meeting of the International Association of Applied Mathematics and Mechanics - GAMM, Magdeburg, Deutschland, 18.-22. March 2024, Oral Presentation S25.01-4

Available at <a href="https://jahrestagung.gamm.org/wp-content/uploads/2024/03/BookOfAbstracts-2.pdf#page=365" target="_blank">Book of Abstracts of the 94th Annual Meeting of the International Association of Applied Mathematics and Mechanics, p363</a>

The other feature selection methods that were compared to in our paper is as listed below:
1. LH-RELIEF: Feature weight estimation for gene selection: a local hyperlinear learning approach
DOI: https://doi.org/10.1186/1471-2105-15-70

2. I-RELIEF: Iterative RELIEF for Feature Weighting: Algorithms, Theories, and Applications
DOI: https://doi.org/10.1109/TPAMI.2007.1093

3. RELIEF-F: Estimating attributes: Analysis and extensions of RELIEF
DOI: https://doi.org/10.1007/3-540-57868-4_57

4. MultiSURF: Benchmarking relief-based feature selection methods for bioinformatics data mining
DOI: https://doi.org/10.1016/j.jbi.2018.07.015

5. Random Forests
DOI: https://doi.org/10.1023/A:1010933404324

6. ANOVA F-statistic: Statistical Methods for Research Workers

7. Mutual Information: Estimating mutual information
DOI: https://doi.org/10.1103/PhysRevE.69.066138
