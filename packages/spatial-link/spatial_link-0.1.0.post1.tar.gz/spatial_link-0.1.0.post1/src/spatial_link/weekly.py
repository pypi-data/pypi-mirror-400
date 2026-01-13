from __future__ import annotations

import numpy as np
import networkx as nx
from typing import Literal, Optional, Tuple


def _split_windows(
    n_days: int,
    days_per_week: int,
    min_days: int,
    drop_last: bool,
) -> list[tuple[int, int]]:
    """
    Returns list of (start, end) day indices for each week window.
    end is exclusive.

    - If drop_last=True: only include FULL windows of length days_per_week.
    - If drop_last=False: include last window only if it has >= min_days days.
    """
    windows: list[tuple[int, int]] = []
    s = 0

    while s < n_days:
        e = min(n_days, s + days_per_week)
        length = e - s

        # not enough for even minimum window
        if length < min_days:
            break

        # require full weeks
        if drop_last and length < days_per_week:
            break

        windows.append((s, e))
        s += days_per_week

    return windows


def _bfs_candidate_edges(
    mean_mat: np.ndarray,
    max_depth: int,
    positive_only: bool,
) -> set[tuple[int, int]]:
    """
    Candidate edges from shortest paths (BFS by hops) up to max_depth
    on the weekly mean matrix.
    """
    n = mean_mat.shape[0]
    G = nx.DiGraph()

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            w = float(mean_mat[i, j])
            if positive_only:
                if w > 0:
                    G.add_edge(i, j)
            else:
                if w != 0:
                    G.add_edge(i, j)

    cand: set[tuple[int, int]] = set()

    # BFS distances up to cutoff, then take one shortest path to collect edges
    for src in range(n):
        lengths = nx.single_source_shortest_path_length(G, src, cutoff=max_depth)
        for dst, dist in lengths.items():
            if dst == src or dist == 0:
                continue
            try:
                path = nx.shortest_path(G, src, dst)
                for k in range(len(path) - 1):
                    cand.add((path[k], path[k + 1]))
            except nx.NetworkXNoPath:
                pass

    return cand


def weekly_spatial_link(
    velocities: np.ndarray,
    *,
    days_per_week: int = 7,
    min_days: Optional[int] = None,
    drop_last_incomplete: bool = True,
    max_depth: int = 4,
    n_mc: int = 100,
    alpha: float = 0.05,
    alternative: Literal["greater", "less"] = "greater",
    positive_only: bool = True,
    null_scope: Literal["window", "global"] = "window",
    seed: int = 0,
    return_pvalues: bool = False,
    return_weighted: bool = False,
) -> Tuple[np.ndarray, list[tuple[int, int]], np.ndarray] | Tuple[np.ndarray, list[tuple[int, int]]]:
    """
    Weekly Spatial-Link (BFS -> Monte Carlo).

    Parameters
    ----------
    velocities:
        Array of shape (n_days, n_regions, n_regions)
    days_per_week:
        Window size (7 typical)
    min_days:
        Minimum days required to include a window.
        If None, defaults to days_per_week (full windows only).
    drop_last_incomplete:
        True -> drop last incomplete window
        False -> include last window only if length >= min_days
    max_depth:
        BFS cutoff (hops)
    n_mc:
        Monte Carlo iterations per candidate edge
    alpha:
        significance threshold
    alternative:
        "greater" -> p = P(null >= obs)
        "less"    -> p = P(null <= obs)
    positive_only:
        consider only values > 0
    null_scope:
        "window" -> pool from current week block (recommended default)
        "global" -> pool from all days (more comparable across weeks)
    seed:
        RNG seed for reproducibility
    return_pvalues:
        if True, return p-values tensor in addition
    return_weighted:
        if True adjacency stores obs weight; else 0/1

    Returns
    -------
    adj_weekly: (n_weeks, n_regions, n_regions)
    windows: list[(start_day, end_day)]
    pvals_weekly (optional): same shape as adj_weekly
    """
    v = np.asarray(velocities)
    if v.ndim != 3 or v.shape[1] != v.shape[2]:
        raise ValueError("velocities must have shape (n_days, n_regions, n_regions)")

    if days_per_week < 1:
        raise ValueError("days_per_week must be >= 1")

    if min_days is None:
        min_days = days_per_week
    if min_days < 1 or min_days > days_per_week:
        raise ValueError("min_days must be in [1, days_per_week]")

    if null_scope not in ("window", "global"):
        raise ValueError("null_scope must be 'window' or 'global'")

    n_days, n_regions, _ = v.shape
    rng = np.random.default_rng(seed)

    # global pool computed once (if requested)
    global_pool = None
    if null_scope == "global":
        if positive_only:
            global_pool = v[v > 0].ravel()
        else:
            global_pool = v[v != 0].ravel()

    windows = _split_windows(
        n_days=n_days,
        days_per_week=days_per_week,
        min_days=min_days,
        drop_last=drop_last_incomplete,
    )

    n_weeks = len(windows)
    adj = np.zeros((n_weeks, n_regions, n_regions), dtype=float)
    pvals = np.ones((n_weeks, n_regions, n_regions), dtype=float) if return_pvalues else None

    for w, (s, e) in enumerate(windows):
        block = v[s:e]                # (k_days, n, n)
        k_days = block.shape[0]
        mean_mat = block.mean(axis=0) # (n, n)

        cand = _bfs_candidate_edges(mean_mat, max_depth=max_depth, positive_only=positive_only)

        # choose pool
        if null_scope == "global":
            pool = global_pool
        else:
            if positive_only:
                pool = block[block > 0].ravel()
            else:
                pool = block[block != 0].ravel()

        if pool is None or pool.size == 0:
            continue

        for (i, j) in cand:
            obs = float(mean_mat[i, j])
            if positive_only and obs <= 0:
                continue
            if (not positive_only) and obs == 0:
                continue

            # null statistic matches weekly mean: mean of k_days sampled values
            null_means = np.empty(n_mc, dtype=float)
            for t in range(n_mc):
                null_means[t] = rng.choice(pool, size=k_days, replace=True).mean()

            if alternative == "greater":
                p = float((null_means >= obs).mean())
            else:
                p = float((null_means <= obs).mean())

            if return_pvalues:
                pvals[w, i, j] = p

            if p < alpha:
                adj[w, i, j] = obs if return_weighted else 1.0

    if return_pvalues:
        return adj, windows, pvals
    return adj, windows
