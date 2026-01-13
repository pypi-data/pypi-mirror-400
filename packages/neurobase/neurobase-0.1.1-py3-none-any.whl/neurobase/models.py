import numpy as np
from collections import Counter
from math import sqrt, exp, inf
import random
from collections import deque
import statistics



# 1. SIMPLE LINEAR REGRESSION (y = m*x + c)
class SimpleLinearRegression:
    def __init__(self):
        self.slope = None
        self.intercept = None

    def fit(self, X, y):
        X = np.array(X).flatten()
        y = np.array(y)

        x_mean = np.mean(X)
        y_mean = np.mean(y)

        numerator = np.sum((X - x_mean) * (y - y_mean))
        denominator = np.sum((X - x_mean) ** 2)

        self.slope = numerator / denominator
        self.intercept = y_mean - self.slope * x_mean
        return self

    def predict(self, X):
        X = np.array(X).flatten()
        return self.slope * X + self.intercept



# 2. MULTIPLE LINEAR REGRESSION (Normal Equation)

class MultipleLinearRegression:
    def __init__(self):
        self.coefficients = None

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        X = np.column_stack((np.ones(X.shape[0]), X))

        self.coefficients = np.linalg.inv(X.T @ X) @ X.T @ y
        return self

    def predict(self, X):
        X = np.array(X)
        X = np.column_stack((np.ones(X.shape[0]), X))
        return X @ self.coefficients



# 3. LOGISTIC REGRESSION (Gradient Descent)

class LogisticRegression:
    def __init__(self, learning_rate=0.01, iterations=1000):
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.weights = None
        self.bias = 0

    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)

        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)

        for _ in range(self.iterations):
            linear = X @ self.weights + self.bias
            predictions = self.sigmoid(linear)

            dw = (1 / n_samples) * (X.T @ (predictions - y))
            db = (1 / n_samples) * np.sum(predictions - y)

            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

        return self

    def predict(self, X):
        linear = X @ self.weights + self.bias
        probs = self.sigmoid(linear)
        return (probs >= 0.5).astype(int)


# 4. RIDGE REGRESSION
class RidgeRegression:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.coefficients = None

    def fit(self, X, y):
        X = np.array(X)
        y = np.array(y)
        X = np.column_stack((np.ones(X.shape[0]), X))

        n_features = X.shape[1]
        I = np.eye(n_features)
        I[0, 0] = 0  # Don't regularize bias

        self.coefficients = np.linalg.inv(X.T @ X + self.alpha * I) @ X.T @ y
        return self

    def predict(self, X):
        X = np.column_stack((np.ones(len(X)), X))
        return X @ self.coefficients


# 5. LASSO REGRESSION (Coordinate Descent)

class LassoRegression:
    def __init__(self, alpha=1.0, max_iter=1000):
        self.alpha = alpha
        self.max_iter = max_iter
        self.coefficients = None

    def fit(self, X, y):
        X = np.column_stack((np.ones(len(X)), X))
        y = np.array(y)
        n_samples, n_features = X.shape

        self.coefficients = np.zeros(n_features)

        for _ in range(self.max_iter):
            for j in range(n_features):
                residual = y - (X @ self.coefficients) + self.coefficients[j] * X[:, j]
                rho = np.dot(X[:, j], residual)

                if j == 0:  
                    self.coefficients[j] = rho / np.sum(X[:, j] ** 2)
                else:
                    self.coefficients[j] = np.sign(rho) * max(0, abs(rho) - self.alpha) / np.sum(X[:, j] ** 2)

        return self

    def predict(self, X):
        X = np.column_stack((np.ones(len(X)), X))
        return X @ self.coefficients


# 6. CUSTOM DECISION TREE REGRESSOR
class DecisionTreeRegressorCustom:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth
        self.tree = None

    def fit(self, X, y):
        self.tree = self._build_tree(np.array(X), np.array(y), depth=0)
        return self

    def predict(self, X):
        return np.array([self._predict_one(row, self.tree) for row in X])

    def _build_tree(self, X, y, depth):
        if len(set(y)) == 1:
            return float(y[0])

        if self.max_depth is not None and depth >= self.max_depth:
            return float(np.mean(y))

        best_feature, best_threshold = self._find_best_split(X, y)
        if best_feature is None:
            return float(np.mean(y))

        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask

        return {
            "feature": best_feature,
            "threshold": best_threshold,
            "left": self._build_tree(X[left_mask], y[left_mask], depth + 1),
            "right": self._build_tree(X[right_mask], y[right_mask], depth + 1)
        }

    def _find_best_split(self, X, y):
        best_feature, best_threshold = None, None
        best_loss = np.inf

        for feature in range(X.shape[1]):
            thresholds = np.unique(X[:, feature])
            for t in thresholds:
                left = y[X[:, feature] <= t]
                right = y[X[:, feature] > t]

                if len(left) == 0 or len(right) == 0:
                    continue

                loss = np.var(left) * len(left) + np.var(right) * len(right)
                if loss < best_loss:
                    best_loss = loss
                    best_feature = feature
                    best_threshold = t

        return best_feature, best_threshold

    def _predict_one(self, x, tree):
        if not isinstance(tree, dict):
            return tree
        if x[tree["feature"]] <= tree["threshold"]:
            return self._predict_one(x, tree["left"])
        else:
            return self._predict_one(x, tree["right"])


# 7. KNN CLASSIFIER
class KNNClassifier:
    def __init__(self, k=3):
        self.k = k

    def fit(self, X, y):
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        return self

    def predict(self, X):
        predictions = []
        for x in X:
            distances = np.linalg.norm(self.X_train - x, axis=1)
            k_idx = np.argsort(distances)[:self.k]
            labels = self.y_train[k_idx]
            predictions.append(Counter(labels).most_common(1)[0][0])
        return np.array(predictions)




# 8. GRADIENT BOOSTING REGRESSOR (Simplified)
class GradientBoostingRegressorCustom:
    def __init__(self, n_estimators=50, lr=0.1):
        self.n_estimators = n_estimators
        self.lr = lr
        self.models = []

    def fit(self, X, y):
        X, y = np.array(X), np.array(y)
        pred = np.zeros(len(y))

        for _ in range(self.n_estimators):
            residual = y - pred
            tree = DecisionTreeRegressorCustom(max_depth=3)
            tree.fit(X, residual)

            update = tree.predict(X)
            pred += self.lr * update
            self.models.append(tree)

        return self

    def predict(self, X):
        X = np.array(X)
        pred = np.zeros(X.shape[0])
        for tree in self.models:
            pred += self.lr * tree.predict(X)
        return pred


def euclidean(a, b):
    if len(a) != len(b):
        raise ValueError("Points must have same dimension")
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

def mean_point(points):
    if not points:
        raise ValueError("Empty points")
    dim = len(points[0])
    return [sum(p[i] for p in points)/len(points) for i in range(dim)]

class KMeans:
    def __init__(self, n_clusters=2, max_iter=100, tol=1e-4, random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.centroids = None
        self.labels_ = None

    def fit(self, X):
        if self.n_clusters <= 0:
            raise ValueError("n_clusters must be positive")
        n = len(X)
        if n == 0:
            raise ValueError("Empty dataset")
        rnd = random.Random(self.random_state)
        self.centroids = [list(x) for x in rnd.sample(X, min(self.n_clusters, n))]
        for it in range(self.max_iter):
            clusters = [[] for _ in range(self.n_clusters)]
            labels = []
            for x in X:
                dists = [euclidean(x, c) for c in self.centroids]
                idx = min(range(len(dists)), key=lambda i: dists[i])
                clusters[idx].append(x)
                labels.append(idx)
            new_centroids = []
            for i, pts in enumerate(clusters):
                if pts:
                    new_centroids.append(mean_point(pts))
                else:
                    new_centroids.append(list(rnd.choice(X)))
            shift = max(euclidean(a, b) for a, b in zip(self.centroids, new_centroids))
            self.centroids = new_centroids
            if shift <= self.tol:
                break
        self.labels_ = labels
        return self

    def predict(self, X):
        if self.centroids is None:
            raise ValueError("Model not fitted")
        labels = []
        for x in X:
            dists = [euclidean(x, c) for c in self.centroids]
            idx = min(range(len(dists)), key=lambda i: dists[i])
            labels.append(idx)
        return labels

class KMedoids:
    def __init__(self, n_clusters=2, max_iter=100, random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state
        self.medoids = None
        self.labels_ = None

    def fit(self, X):
        n = len(X)
        if self.n_clusters <= 0 or self.n_clusters > n:
            raise ValueError("Invalid n_clusters")
        rnd = random.Random(self.random_state)
        medoid_idxs = rnd.sample(range(n), self.n_clusters)
        medoids = [X[i] for i in medoid_idxs]
        for it in range(self.max_iter):
            clusters = [[] for _ in range(self.n_clusters)]
            labels = []
            for x in X:
                dists = [euclidean(x, m) for m in medoids]
                idx = min(range(len(dists)), key=lambda i: dists[i])
                clusters[idx].append(x)
                labels.append(idx)
            changed = False
            for i in range(self.n_clusters):
                best_medoid = medoids[i]
                best_cost = sum(euclidean(x, best_medoid) for x in clusters[i]) if clusters[i] else inf
                for candidate in clusters[i]:
                    if candidate == best_medoid:
                        continue
                    cost = sum(euclidean(x, candidate) for x in clusters[i])
                    if cost < best_cost:
                        best_cost = cost
                        best_medoid = candidate
                        changed = True
                medoids[i] = best_medoid
            if not changed:
                break
        self.medoids = medoids
        self.labels_ = labels
        return self

    def predict(self, X):
        if self.medoids is None:
            raise ValueError("Model not fitted")
        labels = []
        for x in X:
            dists = [euclidean(x, m) for m in self.medoids]
            idx = min(range(len(dists)), key=lambda i: dists[i])
            labels.append(idx)
        return labels

class Agglomerative:
    def __init__(self, linkage='single'):
        if linkage not in ('single', 'complete', 'average'):
            raise ValueError("linkage must be 'single','complete',or 'average'")
        self.linkage = linkage
        self.labels_ = None

    def fit(self, X, n_clusters=2):
        n = len(X)
        if n_clusters <= 0 or n_clusters > n:
            raise ValueError("Invalid n_clusters")
        clusters = {i: [i] for i in range(n)}  # store indices
        # precompute distances
        dist = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1, n):
                d = euclidean(X[i], X[j])
                dist[i][j] = dist[j][i] = d
        while len(clusters) > n_clusters:
            best = (inf, None, None)
            keys = list(clusters.keys())
            for ia, a in enumerate(keys):
                for b in keys[ia+1:]:
                    if self.linkage == 'single':
                        d = min(dist[p][q] for p in clusters[a] for q in clusters[b])
                    elif self.linkage == 'complete':
                        d = max(dist[p][q] for p in clusters[a] for q in clusters[b])
                    else:
                        d = sum(dist[p][q] for p in clusters[a] for q in clusters[b]) / (len(clusters[a]) * len(clusters[b]))
                    if d < best[0]:
                        best = (d, a, b)
            _, a, b = best
            clusters[a].extend(clusters[b])
            del clusters[b]
        labels = [-1]*n
        for label_idx, key in enumerate(clusters):
            for idx in clusters[key]:
                labels[idx] = label_idx
        self.labels_ = labels
        return self

class DBSCAN:
    def __init__(self, eps=0.5, min_samples=5):
        self.eps = eps
        self.min_samples = min_samples
        self.labels_ = None

    def fit(self, X):
        n = len(X)
        labels = [None]*n
        visited = [False]*n
        cluster_id = 0
        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True
            neighbors = [j for j in range(n) if euclidean(X[i], X[j]) <= self.eps]
            if len(neighbors) < self.min_samples:
                labels[i] = -1
                continue
            labels[i] = cluster_id
            seed_set = deque(neighbors)
            while seed_set:
                j = seed_set.popleft()
                if not visited[j]:
                    visited[j] = True
                    j_neighbors = [k for k in range(n) if euclidean(X[j], X[k]) <= self.eps]
                    if len(j_neighbors) >= self.min_samples:
                        for k in j_neighbors:
                            if k not in seed_set:
                                seed_set.append(k)
                if labels[j] is None or labels[j] == -1:
                    labels[j] = cluster_id
            cluster_id += 1
        self.labels_ = labels
        return self

class OPTICS:
    def __init__(self, eps=float('inf'), min_samples=5):
        self.eps = eps
        self.min_samples = min_samples
        self.ordering = []
        self.reachability = []

    def fit(self, X):
        n = len(X)
        visited = [False]*n
        reach = [inf]*n
        ordering = []
        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True
            ordering.append(i)
            neighbors = [j for j in range(n) if euclidean(X[i], X[j]) <= self.eps]
            if len(neighbors) >= self.min_samples:
                dists = sorted(euclidean(X[i], X[j]) for j in neighbors)
                core_dist = dists[self.min_samples-1]
                for j in neighbors:
                    if not visited[j]:
                        new_reach = max(core_dist, euclidean(X[i], X[j]))
                        if new_reach < reach[j]:
                            reach[j] = new_reach
            for j in neighbors:
                if not visited[j]:
                    visited[j] = True
                    ordering.append(j)
        self.ordering = ordering
        self.reachability = reach
        return self

class GMM:
    def __init__(self, n_components=2, max_iter=100, tol=1e-4, random_state=None):
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.weights_ = None
        self.means_ = None
        self.vars_ = None
        self.resp_ = None

    def _gaussian_pdf(self, x, mean, var):
        dim = len(x)
        coef = 1.0
        for vi in var:
            coef *= (1.0 / sqrt(2 * 3.141592653589793 * vi)) if vi > 0 else 0.0
        exp_term = 0.0
        for xi, mu, vi in zip(x, mean, var):
            if vi <= 0:
                return 0.0
            exp_term += ((xi - mu) ** 2) / (2 * vi)
        return coef * exp(-exp_term)

    def fit(self, X):
        n = len(X)
        if n == 0:
            raise ValueError("Empty dataset")
        dim = len(X[0])
        rnd = random.Random(self.random_state)
        means = [list(x) for x in rnd.sample(X, min(self.n_components, n))]
        weights = [1.0 / self.n_components] * self.n_components
        vars_ = [[1.0 for _ in range(dim)] for _ in range(self.n_components)]
        for it in range(self.max_iter):
            resp = [[0.0]*self.n_components for _ in range(n)]
            for i, x in enumerate(X):
                total = 0.0
                for k in range(self.n_components):
                    p = weights[k] * self._gaussian_pdf(x, means[k], vars_[k])
                    resp[i][k] = p
                    total += p
                if total == 0.0:
                    for k in range(self.n_components):
                        resp[i][k] = 1.0 / self.n_components
                else:
                    for k in range(self.n_components):
                        resp[i][k] /= total
            Nk = [sum(resp[i][k] for i in range(n)) for k in range(self.n_components)]
            new_means = []
            new_vars = []
            new_weights = []
            for k in range(self.n_components):
                if Nk[k] == 0:
                    new_means.append(means[k])
                    new_vars.append(vars_[k])
                    new_weights.append(0.0)
                    continue
                mean_k = [0.0]*dim
                for i in range(n):
                    for d in range(dim):
                        mean_k[d] += resp[i][k] * X[i][d]
                mean_k = [v / Nk[k] for v in mean_k]
                var_k = [0.0]*dim
                for i in range(n):
                    for d in range(dim):
                        var_k[d] += resp[i][k] * ((X[i][d] - mean_k[d])**2)
                var_k = [v / Nk[k] for v in var_k]
                new_means.append(mean_k)
                var_k = [max(v, 1e-6) for v in var_k]
                new_vars.append(var_k)
                new_weights.append(Nk[k]/n)
            shift = max(euclidean(a,b) for a,b in zip(means, new_means))
            means, vars_, weights = new_means, new_vars, new_weights
            if shift <= self.tol:
                break
        self.means_ = means
        self.vars_ = vars_
        self.weights_ = weights
        self.resp_ = resp
        return self

    def predict(self, X):
        if self.means_ is None:
            raise ValueError("Model not fitted")
        labels = []
        for x in X:
            probs = []
            for k in range(self.n_components):
                probs.append(self.weights_[k] * self._gaussian_pdf(x, self.means_[k], self.vars_[k]))
            total = sum(probs)
            if total == 0:
                labels.append(0)
            else:
                labels.append(max(range(len(probs)), key=lambda i: probs[i]))
        return labels

class MeanShift:
    def __init__(self, bandwidth=1.0, max_iter=100, tol=1e-3):
        self.bandwidth = bandwidth
        self.max_iter = max_iter
        self.tol = tol
        self.centroids = None

    def fit(self, X):
        if not X:
            raise ValueError("Empty dataset")
        centroids = [list(x) for x in X]
        for it in range(self.max_iter):
            new_centroids = []
            for c in centroids:
                in_band = [x for x in X if euclidean(x, c) <= self.bandwidth]
                if not in_band:
                    new_centroids.append(c)
                else:
                    new_centroids.append(mean_point(in_band))
            merged = []
            for c in new_centroids:
                if not any(euclidean(c, m) < self.tol for m in merged):
                    merged.append(c)
            # ensure we compare matching lengths
            L = min(len(merged), len(centroids))
            shift = 0.0
            if L>0:
                shift = max(euclidean(a,b) for a,b in zip(centroids[:L], merged[:L]))
            centroids = merged
            if shift <= self.tol:
                break
        self.centroids = centroids
        return self

    def predict(self, X):
        if self.centroids is None:
            raise ValueError("Model not fitted")
        labels = []
        for x in X:
            dists = [euclidean(x, c) for c in self.centroids]
            labels.append(min(range(len(dists)), key=lambda i: dists[i]))
        return labels

class AffinityPropagation:
    def __init__(self, max_iter=100, damping=0.5):
        self.max_iter = max_iter
        self.damping = damping
        self.cluster_centers_ = None
        self.labels_ = None

    def fit(self, X):
        n = len(X)
        if n == 0:
            raise ValueError("Empty dataset")
        s = [[-euclidean(X[i], X[j]) for j in range(n)] for i in range(n)]
        all_vals = [s[i][j] for i in range(n) for j in range(n)]
        pref = statistics.median(all_vals)
        for i in range(n):
            s[i][i] = pref
        a = [[0.0]*n for _ in range(n)]
        r = [[0.0]*n for _ in range(n)]
        for it in range(self.max_iter):
            for i in range(n):
                for j in range(n):
                    max_val = -inf
                    for k in range(n):
                        if k == j:
                            continue
                        val = a[i][k] + s[i][k]
                        if val > max_val:
                            max_val = val
                    newr = s[i][j] - max_val
                    r[i][j] = (1 - self.damping) * newr + self.damping * r[i][j]
            for i in range(n):
                for j in range(n):
                    if i == j:
                        rp = sum(max(0, r[k][j]) for k in range(n) if k != j)
                        newa = rp
                    else:
                        newa = min(0, r[j][j] + sum(max(0, r[k][j]) for k in range(n) if k not in (i,j)))
                    a[i][j] = (1 - self.damping) * newa + self.damping * a[i][j]
        exemplars = [j for j in range(n) if r[j][j] + a[j][j] > 0]
        if not exemplars:
            exemplars = [max(range(n), key=lambda j: r[j][j] + a[j][j])]
        centers = [X[j] for j in exemplars]
        labels = []
        for i in range(n):
            labels.append(min(range(len(centers)), key=lambda k: euclidean(X[i], centers[k])))
        self.cluster_centers_ = centers
        self.labels_ = labels
        return self

class SpectralClustering:
    def __init__(self, n_clusters=2, n_iter=100, random_state=None):
        self.n_clusters = n_clusters
        self.n_iter = n_iter
        self.random_state = random_state
        self.labels_ = None

    def fit(self, X):
        n = len(X)
        if n == 0:
            raise ValueError("Empty dataset")
        dists = [[0.0]*n for _ in range(n)]
        maxd = 0.0
        for i in range(n):
            for j in range(i+1, n):
                d = euclidean(X[i], X[j])
                dists[i][j] = dists[j][i] = d
                if d > maxd: maxd = d
        sigma = maxd/2 if maxd>0 else 1.0
        W = [[exp(-(dists[i][j]**2)/(2*sigma*sigma)) for j in range(n)] for i in range(n)]
        D = [sum(W[i]) for i in range(n)]
        M = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if D[i] > 0 and D[j] > 0:
                    M[i][j] = W[i][j] / sqrt(D[i]*D[j])
                else:
                    M[i][j] = 0.0
        rnd = random.Random(self.random_state)
        vectors = []
        for k in range(self.n_clusters):
            v = [rnd.random() for _ in range(n)]
            for it in range(self.n_iter):
                mv = [sum(M[i][j]*v[j] for j in range(n)) for i in range(n)]
                for u in vectors:
                    proj = sum(mv[i]*u[i] for i in range(n)) / (sum(u_i*u_i for u_i in u) + 1e-12)
                    mv = [mv[i] - proj*u[i] for i,u in enumerate(u)]
                norm = sqrt(sum(x*x for x in mv))
                if norm == 0:
                    break
                v = [x/norm for x in mv]
            vectors.append(v)
        rows = [[vec[i] for vec in vectors] for i in range(n)]
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        kmeans.fit(rows)
        self.labels_ = kmeans.labels_
        return self
