#!/usr/bin/env python3
"""
Fast estimation of pairwise column dependencies for attention head configuration.

Uses chi-squared tests on sampled pairs to estimate the number of dependent
column relationships without exhaustively testing all C(n,2) pairs.

Caches results in SQLite for reuse across training runs on the same dataset.
"""
import hashlib
import json
import logging
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional, Set

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ==============================================================================
# RELATIONSHIP ESTIMATION CACHE
# ==============================================================================

def _get_featrix_root():
    """Get Featrix root directory."""
    if Path("/sphere/app").exists():
        return "/sphere"
    root = os.environ.get("FEATRIX_ROOT")
    if root:
        return root
    return str(Path.home() / "sphere-workspace")

FEATRIX_ROOT = _get_featrix_root()
RELATIONSHIP_CACHE_DIR = Path(FEATRIX_ROOT) / "app" / "featrix_output" / ".relationship_cache"
RELATIONSHIP_CACHE_FILE = RELATIONSHIP_CACHE_DIR / "relationship_estimation.db"


class RelationshipEstimationCache:
    """SQLite cache for relationship estimation results."""
    
    def __init__(self, cache_file: Path = RELATIONSHIP_CACHE_FILE):
        self.cache_file = cache_file
        self.enabled = True
        
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(
                str(self.cache_file),
                timeout=10.0,
                check_same_thread=False
            )
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA journal_mode=WAL")
            
            # Create cache table with columns_json for fuzzy matching
            # Cache key is now just a unique ID, matching is done by column overlap
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationship_cache (
                    cache_key TEXT PRIMARY KEY,
                    columns_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    n_cols INTEGER NOT NULL,
                    n_rows INTEGER NOT NULL,
                    estimated_edges INTEGER NOT NULL,
                    elapsed_seconds REAL NOT NULL
                )
            """)
            # Add columns_json column if it doesn't exist (migration for existing DBs)
            try:
                self.cursor.execute("ALTER TABLE relationship_cache ADD COLUMN columns_json TEXT")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists
            self.conn.commit()
            logger.debug(f"✅ Relationship cache initialized: {self.cache_file}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize relationship cache: {e}")
            self.enabled = False
            self.conn = None
            self.cursor = None
    
    def _column_match_ratio(self, cols1: Set, cols2: Set) -> float:
        """Calculate what fraction of cols1 are present in cols2."""
        if not cols1:
            return 0.0
        return len(cols1 & cols2) / len(cols1)
    
    def _make_column_signature(self, df: pd.DataFrame) -> str:
        """Create a signature from sorted column names for storage."""
        return json.dumps(sorted(df.columns.tolist()), sort_keys=True)
    
    def get(
        self,
        df: pd.DataFrame,
        n_pairs: int = None,  # Unused - kept for backward compat
        repeat: int = None,   # Unused - kept for backward compat
        max_pairs: int = None,  # Unused - kept for backward compat
        n_bins: int = None,   # Unused - kept for backward compat
        random_state: Optional[int] = None,  # Unused - kept for backward compat
        min_column_match: float = 0.80
    ) -> Optional[dict]:
        """Get cached result using fuzzy column matching.
        
        Relationship estimation depends on schema (columns), not row order.
        If >= 80% of columns match a cached entry, we reuse it.
        
        The n_pairs/repeat/max_pairs/n_bins/random_state params are ignored -
        matching is purely based on column schema overlap.
        """
        if not self.enabled:
            logger.info(f"🔍 Relationship cache: DISABLED")
            return None
        
        try:
            current_cols = set(df.columns)
            n_cols = len(current_cols)
            
            # Log cache file location
            logger.info(f"🔍 Relationship cache: checking {self.cache_file} (n_cols={n_cols})")
            
            # Fetch all cached entries (there shouldn't be many - one per unique schema)
            self.cursor.execute(
                "SELECT columns_json, result_json, elapsed_seconds, n_cols FROM relationship_cache"
            )
            rows = self.cursor.fetchall()
            
            logger.info(f"   Found {len(rows)} cached entries")
            
            best_match = None
            best_ratio = 0.0
            
            for row in rows:
                columns_json, result_json, elapsed, cached_n_cols = row
                if columns_json is None:
                    continue  # Old entry without columns_json
                
                try:
                    cached_cols = set(json.loads(columns_json))
                except (json.JSONDecodeError, TypeError):
                    continue
                
                # Calculate bidirectional overlap (how similar are the schemas?)
                # We want: most of our columns are in cached, and cached isn't way bigger
                overlap = len(current_cols & cached_cols)
                ratio = overlap / max(n_cols, len(cached_cols))
                
                logger.info(f"   Entry: {cached_n_cols} cols, overlap={overlap}, ratio={ratio:.2f} (need >= {min_column_match:.2f})")
                
                if ratio >= min_column_match and ratio > best_ratio:
                    best_ratio = ratio
                    best_match = (result_json, elapsed, ratio, len(cached_cols))
            
            if best_match:
                result_json, elapsed, ratio, cached_n_cols = best_match
                result = json.loads(result_json)
                logger.info(f"✅ Relationship estimation: CACHE HIT ({ratio*100:.0f}% column match, saved ~{elapsed:.0f}s)")
                logger.info(f"   Using cached result: {result['summary']['estimated_edges_median']} relationships detected")
                logger.info(f"   Current cols: {n_cols}, Cached cols: {cached_n_cols}")
                return result
            
            # Log cache miss (at INFO level for visibility)
            logger.info(f"🔍 Relationship estimation: CACHE MISS (n_cols={n_cols}, checked {len(rows)} entries, none >= {min_column_match*100:.0f}% match)")
            return None
        except Exception as e:
            logger.warning(f"⚠️  Relationship cache read failed: {e}")
            return None
    
    def set(
        self,
        df: pd.DataFrame,
        n_pairs: int,
        repeat: int,
        max_pairs: int,
        n_bins: int,
        random_state: Optional[int],
        result: dict,
        elapsed_seconds: float
    ):
        """Cache result with column signature for fuzzy matching."""
        if not self.enabled:
            return
        
        try:
            columns_json = self._make_column_signature(df)
            # Use hash of columns as cache key (for uniqueness, not matching)
            cache_key = hashlib.sha256(columns_json.encode()).hexdigest()
            summary = result.get("summary", {})
            
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO relationship_cache 
                (cache_key, columns_json, result_json, created_at, n_cols, n_rows, estimated_edges, elapsed_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    columns_json,
                    json.dumps(result),
                    time.time(),
                    len(df.columns),
                    len(df),
                    summary.get("estimated_edges_median", 0),
                    elapsed_seconds
                )
            )
            self.conn.commit()
            logger.info(f"💾 Cached relationship estimation result (took {elapsed_seconds:.1f}s, {len(df.columns)} columns)")
        except Exception as e:
            logger.warning(f"⚠️  Relationship cache write failed: {e}")


# Global cache instance (lazy initialization)
_relationship_cache: Optional[RelationshipEstimationCache] = None

def _get_cache() -> RelationshipEstimationCache:
    """Get or create global cache instance."""
    global _relationship_cache
    if _relationship_cache is None:
        _relationship_cache = RelationshipEstimationCache()
    return _relationship_cache


def estimate_pairwise_dependency_count_fast(
    df: pd.DataFrame,
    *,
    n_pairs: int = 600,
    repeat: int = 5,
    max_pairs: int = 5_000,
    target_error: float = 0.03,
    n_bins: int = 8,
    lambda_storey: float = 0.8,
    min_joint_n: int = 30,
    random_state=None,
    use_cache: bool = True,
):
    """
    Fast estimate of #dependent column pairs.

    Approach:
      - Repeats 'repeat' times:
          - sample up to m pairs (without enumerating all C(p,2) pairs)
          - chi^2 independence on (possibly binned) contingency table
          - Storey estimator to infer π0 (null fraction), so edges ≈ (1-π0)*C(p,2)
      - Returns per-run results + median + [min,max] range

    Good for large p (hundreds/thousands): sampling is O(m), not O(p^2).
    
    Results are cached in SQLite to avoid re-computation on the same dataset.
    
    Args:
        df: DataFrame to analyze
        n_pairs: Base number of pairs to sample per run (default: 600)
        repeat: Number of sampling runs (default: 5)
        max_pairs: Maximum pairs to test (default: 5000)
        target_error: Target margin of error for proportion estimation (default: 0.03)
        n_bins: Number of bins for quantizing numeric columns (default: 8)
        lambda_storey: Threshold for Storey estimator (default: 0.8)
        min_joint_n: Minimum samples required for chi-squared test (default: 30)
        random_state: Random seed for reproducibility
        use_cache: Whether to use caching (default: True)
    
    Returns:
        dict with 'summary' and 'runs':
        - summary: Dict with median/min/max estimates
        - runs: List of individual run results
    """
    from scipy.stats import chi2_contingency
    
    # Check cache first
    if use_cache:
        cache = _get_cache()
        cached_result = cache.get(df, n_pairs, repeat, max_pairs, n_bins, random_state)
        if cached_result is not None:
            return cached_result
    
    estimation_start_time = time.time()
    
    rng = np.random.default_rng(random_state)

    cols = list(df.columns)
    p = len(cols)
    M = p * (p - 1) // 2
    if M == 0:
        return {
            "summary": dict(
                n_cols=p, total_pairs=0, estimated_edges_median=0,
                pi1_median=0.0, tested_pairs_median=0
            ),
            "runs": []
        }

    # Precompute dtype flags once
    is_num = {c: pd.api.types.is_numeric_dtype(df[c]) for c in cols}

    # Worst-case sample size for ±target_error on a proportion at 95% confidence
    m_required = int(np.ceil(0.25 * (1.96 / target_error) ** 2))
    m_base = max(n_pairs, m_required)
    m_base = min(max_pairs, M, m_base)

    def sample_unique_pairs(num_pairs: int, local_rng: np.random.Generator):
        """Sample unique unordered (i<j) pairs without enumerating all combinations."""
        seen = set()
        out = []
        # Oversample to reduce loop iterations
        while len(out) < num_pairs:
            need = num_pairs - len(out)
            i = local_rng.integers(0, p, size=need * 4)
            j = local_rng.integers(0, p, size=need * 4)
            for a, b in zip(i, j):
                if a == b:
                    continue
                if a > b:
                    a, b = b, a
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                out.append(key)
                if len(out) >= num_pairs:
                    break
        return out

    def run_once(seed_offset: int):
        local_rng = np.random.default_rng(None if random_state is None else random_state + seed_offset)

        # If small, just test all pairs
        if M <= m_base:
            pairs = [(i, j) for i in range(p) for j in range(i + 1, p)]
        else:
            pairs = sample_unique_pairs(m_base, local_rng)

        pvals = []
        tested = 0
        total_pairs = len(pairs)
        
        # Log progress every 25% or every 500 pairs, whichever is less frequent (to avoid spam)
        progress_interval = max(500, total_pairs // 4) if total_pairs > 1000 else max(100, total_pairs // 4)
        last_logged = 0

        for pair_idx, (i, j) in enumerate(pairs):
            # Log progress periodically
            if pair_idx > 0 and (pair_idx % progress_interval == 0 or pair_idx == total_pairs - 1):
                pct = (pair_idx / total_pairs) * 100
                logger.info(f"      Progress: {pair_idx+1}/{total_pairs} pairs ({pct:.0f}%)...")
                last_logged = pair_idx
            c1, c2 = cols[i], cols[j]
            x = df[c1]
            y = df[c2]

            mask = x.notna() & y.notna()
            if mask.sum() < min_joint_n:
                continue

            x = x[mask]
            y = y[mask]

            # Bin numeric columns into quantiles
            if is_num[c1]:
                try:
                    x = pd.qcut(x, q=n_bins, duplicates="drop")
                except (ValueError, TypeError):
                    continue
            else:
                # Bin high-cardinality categoricals/strings
                n_unique_x = x.nunique()
                if n_unique_x > n_bins * 2:  # High cardinality
                    # Use frequency-based binning: group rare values together
                    value_counts = x.value_counts()
                    # Top n_bins-1 values get their own bins, rest go to "OTHER"
                    top_values = value_counts.head(n_bins - 1).index
                    x = x.apply(lambda v: v if v in top_values else "__OTHER__")
            
            if is_num[c2]:
                try:
                    y = pd.qcut(y, q=n_bins, duplicates="drop")
                except (ValueError, TypeError):
                    continue
            else:
                # Bin high-cardinality categoricals/strings
                n_unique_y = y.nunique()
                if n_unique_y > n_bins * 2:  # High cardinality
                    value_counts = y.value_counts()
                    top_values = value_counts.head(n_bins - 1).index
                    y = y.apply(lambda v: v if v in top_values else "__OTHER__")

            tab = pd.crosstab(x, y)
            if tab.shape[0] < 2 or tab.shape[1] < 2:
                continue

            try:
                _, pval, _, _ = chi2_contingency(tab, correction=False)
            except Exception:
                continue

            pvals.append(pval)
            tested += 1

        if tested == 0:
            pi0_hat = 1.0
        else:
            pvals = np.asarray(pvals)
            pi0_hat = float(np.mean(pvals > lambda_storey) / (1.0 - lambda_storey))
            pi0_hat = float(np.clip(pi0_hat, 0.0, 1.0))

        pi1_hat = 1.0 - pi0_hat
        estimated_edges = int(round(pi1_hat * M))

        return dict(
            requested_pairs=m_base,
            tested_pairs=tested,
            pi0_hat=pi0_hat,
            pi1_hat=pi1_hat,
            estimated_edges=estimated_edges,
        )

    # Run estimation multiple times for robustness
    total_pairs_to_test = repeat * m_base
    logger.info(f"   Running {repeat} estimation runs, {m_base} pairs per run ({total_pairs_to_test} total pairs)...")
    logger.info(f"   Estimated time: ~{total_pairs_to_test * 0.001:.0f} seconds (rough estimate)")
    start_time = time.time()
    runs = []
    for r in range(repeat):
        run_start = time.time()
        logger.info(f"   Run {r+1}/{repeat}: Testing {m_base} pairs...")
        result = run_once(r)
        runs.append(result)
        run_elapsed = time.time() - run_start
        remaining_runs = repeat - (r + 1)
        estimated_remaining = run_elapsed * remaining_runs if remaining_runs > 0 else 0
        logger.info(f"   Run {r+1}/{repeat} complete: {result['tested_pairs']} pairs tested, {result['estimated_edges']} relationships detected ({run_elapsed:.1f}s)")
        if remaining_runs > 0:
            logger.info(f"      ~{estimated_remaining:.0f} seconds remaining")
    
    total_elapsed = time.time() - start_time
    logger.info(f"   ✅ All {repeat} runs complete in {total_elapsed:.1f} seconds")
    
    # Check if any runs completed successfully
    valid_runs = [r for r in runs if r['tested_pairs'] > 0]
    if not valid_runs:
        logger.error(f"💥 Relationship estimation FAILED: No valid chi-squared tests completed")
        logger.error(f"   All {repeat} runs failed to test any pairs")
        logger.error(f"   This indicates a serious data quality issue or bug")
        raise ValueError(f"Relationship estimation failed: no valid tests in {repeat} runs")
    
    if len(valid_runs) < repeat:
        logger.warning(f"⚠️  Only {len(valid_runs)}/{repeat} runs succeeded")

    edges = np.array([r["estimated_edges"] for r in valid_runs], dtype=float)
    pi1s  = np.array([r["pi1_hat"] for r in valid_runs], dtype=float)
    tested = np.array([r["tested_pairs"] for r in valid_runs], dtype=float)
    
    # Log per-run results for transparency
    logger.debug(f"   Run results: tested_pairs={tested.tolist()}, estimated_edges={edges.tolist()}")

    summary = dict(
        n_cols=p,
        total_pairs=M,
        repeat=repeat,
        successful_runs=len(valid_runs),
        requested_pairs_per_run=m_base,
        tested_pairs_median=int(np.median(tested)),
        tested_pairs_min=int(np.min(tested)),
        tested_pairs_max=int(np.max(tested)),
        pi1_median=float(np.median(pi1s)),
        pi1_min=float(np.min(pi1s)),
        pi1_max=float(np.max(pi1s)),
        estimated_edges_median=int(np.median(edges)),
        estimated_edges_min=int(np.min(edges)),
        estimated_edges_max=int(np.max(edges)),
        lambda_storey=lambda_storey,
        n_bins=n_bins,
        min_joint_n=min_joint_n,
        note="Estimated edges are 'pairwise dependence' count; indirect dependencies are included."
    )
    
    logger.debug(f"   ✅ Estimation complete: {summary['estimated_edges_median']} relationships detected")

    result = {"summary": summary, "runs": runs}
    
    # Cache the result for future reuse
    if use_cache:
        total_elapsed = time.time() - estimation_start_time
        cache = _get_cache()
        cache.set(df, n_pairs, repeat, max_pairs, n_bins, random_state, result, total_elapsed)
    
    return result

