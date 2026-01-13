#!/usr/bin/env python3
"""
LLM-based schema analysis using cache.featrix.com API.

Provides functions to query the LLM API for semantic column analysis,
including hybrid column detection, data type inference, and more.

Zero neural dependencies - only uses requests for HTTP calls.
"""

import json
import logging
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Cache for target column suggestions
def _get_featrix_root():
    """Get Featrix root directory for cache storage."""
    try:
        from featrix.neural.platform_utils import featrix_get_root
        return featrix_get_root()
    except Exception:
        return str(Path.home() / "sphere-workspace")

FEATRIX_ROOT = _get_featrix_root()
TARGET_COLUMN_CACHE_DIR = Path(FEATRIX_ROOT) / "app" / "featrix_output" / ".target_column_cache"
TARGET_COLUMN_CACHE_FILE = TARGET_COLUMN_CACHE_DIR / "llm_target_suggestions.db"


class TargetColumnCache:
    """SQLite cache for LLM target column suggestions."""
    
    def __init__(self, cache_file: Path = TARGET_COLUMN_CACHE_FILE):
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
            
            # Create cache table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS target_suggestions_cache (
                    cache_key TEXT PRIMARY KEY,
                    suggestions_result TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    column_count INTEGER NOT NULL
                )
            """)
            self.conn.commit()
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize target column cache: {e}")
            self.enabled = False
            self.cursor = None
    
    def _make_cache_key(self, columns: List[str]) -> str:
        """Generate deterministic cache key from column list."""
        sorted_cols = sorted(columns)
        schema_repr = json.dumps({"columns": sorted_cols}, sort_keys=True)
        return hashlib.sha256(schema_repr.encode()).hexdigest()
    
    def get(self, columns: List[str]) -> Optional[Dict]:
        """Get cached target suggestions."""
        if not self.enabled:
            return None
        
        try:
            cache_key = self._make_cache_key(columns)
            self.cursor.execute(
                "SELECT suggestions_result FROM target_suggestions_cache WHERE cache_key = ?",
                (cache_key,)
            )
            row = self.cursor.fetchone()
            
            if row:
                logger.info(f"✅ Target column suggestions: cache hit (key={cache_key[:16]}...)")
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.warning(f"⚠️  Target cache read failed: {e}")
            return None
    
    def set(self, columns: List[str], result: Dict):
        """Cache target suggestions."""
        if not self.enabled:
            return
        
        try:
            cache_key = self._make_cache_key(columns)
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO target_suggestions_cache 
                (cache_key, suggestions_result, created_at, column_count)
                VALUES (?, ?, ?, ?)
                """,
                (cache_key, json.dumps(result), time.time(), len(columns))
            )
            self.conn.commit()
            num_targets = len(result.get('targets', []))
            logger.info(f"💾 Cached target suggestions (key={cache_key[:16]}..., {num_targets} targets)")
        except Exception as e:
            logger.warning(f"⚠️  Target cache write failed: {e}")
    
    def delete(self, columns: List[str]):
        """Delete a cached target suggestion result (e.g., if it contains an error)."""
        if not self.enabled:
            return
        
        try:
            cache_key = self._make_cache_key(columns)
            self.cursor.execute(
                "DELETE FROM target_suggestions_cache WHERE cache_key = ?",
                (cache_key,)
            )
            self.conn.commit()
            logger.info(f"🗑️  Deleted bad cached target suggestions (key={cache_key[:16]}...)")
        except Exception as e:
            logger.warning(f"⚠️  Target cache delete failed: {e}")


# Global cache instance (lazy initialization)
_target_cache: Optional[TargetColumnCache] = None

def _get_target_cache() -> TargetColumnCache:
    """Get or create global target column cache."""
    global _target_cache
    if _target_cache is None:
        _target_cache = TargetColumnCache()
    return _target_cache


# ============================================================================
# ORDINAL CATEGORY DETECTION
# ============================================================================

ORDINAL_CACHE_DIR = Path(FEATRIX_ROOT) / "app" / "featrix_output" / ".ordinal_cache"
ORDINAL_CACHE_FILE = ORDINAL_CACHE_DIR / "llm_ordinal_detection.db"


class OrdinalCache:
    """SQLite cache for LLM ordinal category detection results.
    
    Opens read-only for reads, reopens as read-write only when writing.
    """
    
    def __init__(self, cache_file: Path = ORDINAL_CACHE_FILE):
        self.cache_file = cache_file
        self.enabled = True
        self.conn = None
        
        try:
            # Create directory and initialize DB with a RW connection first
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
            # Now open read-only for normal reads
            self._open_readonly()
        except Exception as e:
            logger.warning(f"⚠️  Ordinal cache disabled: {e}")
            self.enabled = False
            self.conn = None
    
    def _init_db(self):
        """Initialize database schema (requires RW)."""
        conn = sqlite3.connect(str(self.cache_file), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordinal_cache (
                cache_key TEXT PRIMARY KEY,
                ordinal_result TEXT NOT NULL,
                created_at REAL NOT NULL,
                column_name TEXT NOT NULL,
                category_count INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def _open_readonly(self):
        """Open connection in read-only mode."""
        if self.conn:
            self.conn.close()
        # file: URI with mode=ro for read-only
        uri = f"file:{self.cache_file}?mode=ro"
        self.conn = sqlite3.connect(uri, uri=True, timeout=10.0, check_same_thread=False)
    
    def _do_write(self, sql: str, params: tuple):
        """Open RW connection, execute write, close it."""
        conn = sqlite3.connect(str(self.cache_file), timeout=10.0, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
    
    def _make_cache_key(self, column_name: str, category_values: List[str]) -> str:
        """Generate deterministic cache key from column name and category values."""
        sorted_vals = sorted(category_values)
        schema_repr = json.dumps({"column": column_name, "values": sorted_vals}, sort_keys=True)
        return hashlib.sha256(schema_repr.encode()).hexdigest()
    
    def get(self, column_name: str, category_values: List[str]) -> Optional[Dict]:
        """Get cached ordinal detection result."""
        if not self.enabled or not self.conn:
            return None
        
        try:
            cache_key = self._make_cache_key(column_name, category_values)
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT ordinal_result FROM ordinal_cache WHERE cache_key = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            
            if row:
                logger.debug(f"✅ Ordinal cache hit for '{column_name}' (key={cache_key[:12]}...)")
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.warning(f"⚠️  Ordinal cache read failed: {e}")
            return None
    
    def set(self, column_name: str, category_values: List[str], result: Dict):
        """Cache ordinal detection result (opens RW connection temporarily)."""
        if not self.enabled:
            return
        
        try:
            cache_key = self._make_cache_key(column_name, category_values)
            self._do_write(
                """
                INSERT OR REPLACE INTO ordinal_cache 
                (cache_key, ordinal_result, created_at, column_name, category_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (cache_key, json.dumps(result), time.time(), column_name, len(category_values))
            )
            is_ordinal = result.get('is_ordinal', False)
            logger.debug(f"💾 Cached ordinal result for '{column_name}' (ordinal={is_ordinal})")
        except Exception as e:
            logger.warning(f"⚠️  Ordinal cache write failed: {e}")
    
    def delete(self, column_name: str, category_values: List[str]):
        """Delete a cached ordinal detection result (opens RW connection temporarily)."""
        if not self.enabled:
            return
        
        try:
            cache_key = self._make_cache_key(column_name, category_values)
            self._do_write(
                "DELETE FROM ordinal_cache WHERE cache_key = ?",
                (cache_key,)
            )
            logger.info(f"🗑️  Deleted bad cached result for '{column_name}' (key={cache_key[:12]}...)")
        except Exception as e:
            logger.warning(f"⚠️  Ordinal cache delete failed: {e}")


# Global ordinal cache instance
_ordinal_cache: Optional[OrdinalCache] = None

def _get_ordinal_cache() -> OrdinalCache:
    """Get or create global ordinal cache."""
    global _ordinal_cache
    if _ordinal_cache is None:
        _ordinal_cache = OrdinalCache()
    return _ordinal_cache


def detect_ordinal_categories(
    column_name: str, 
    category_values: List[str],
    sample_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Ask LLM to detect if a categorical column has ordinal (ordered) semantics.
    
    Uses caching to avoid re-querying the same column/value combinations.
    
    Args:
        column_name: Name of the categorical column
        category_values: List of category value strings (e.g., ["low", "medium", "high"])
        sample_context: Optional context about the data (e.g., "credit risk dataset")
    
    Returns:
        Dict with:
            - is_ordinal: bool - whether the categories have natural ordering
            - ordered_values: List[str] - categories in ascending order (if ordinal)
            - confidence: float - 0.0 to 1.0
            - reasoning: str - explanation of the decision
            - order_type: str - "ascending" | "descending" | "custom" | None
    
    Example:
        >>> result = detect_ordinal_categories("credit_rating", ["poor", "fair", "good", "excellent"])
        >>> if result['is_ordinal']:
        >>>     print(f"Order: {result['ordered_values']}")  # ['poor', 'fair', 'good', 'excellent']
    """
    # Check cache first
    cache = _get_ordinal_cache()
    cached_result = cache.get(column_name, category_values)
    if cached_result:
        # Validate cached result - reject if it contains an error or is malformed
        has_error = 'error' in cached_result
        is_ordinal = cached_result.get('is_ordinal', False)
        ordered_values = cached_result.get('ordered_values')
        
        if has_error:
            # Cached result contains HTTP error response - delete and retry
            logger.warning(f"⚠️  Cached result for '{column_name}' contains error, deleting and retrying: {cached_result.get('error', 'unknown')[:100]}")
            cache.delete(column_name, category_values)
            # Don't return - fall through to recompute
        elif is_ordinal and not ordered_values:
            logger.warning(f"⚠️  Rejecting bad cached ordinal result for '{column_name}' (is_ordinal=True but no ordered_values)")
            cache.delete(column_name, category_values)
            # Don't return - fall through to recompute
        else:
            return cached_result
    
    # FAST PATH: If all values are numeric strings, just sort them - no LLM needed
    try:
        sorted_numeric = sorted(category_values, key=lambda x: float(x))
        result = {
            "is_ordinal": True,
            "ordered_values": sorted_numeric,
            "confidence": 1.0,
            "reasoning": "All values are numeric - sorted numerically",
            "order_type": "ascending"
        }
        logger.info(f"   ✅ Ordinal detection (numeric fast path): {len(category_values)} numeric values")
        cache.set(column_name, category_values, result)
        return result
    except (ValueError, TypeError):
        pass  # Not all numeric, continue to LLM
    
    try:
        import requests
    except ImportError:
        logger.error("requests library not available - cannot call cache.featrix.com API")
        return _fallback_ordinal_detection(column_name, category_values)
    
    api_url = "https://cache.featrix.com/query-schema"
    
    # Build prompt for ordinal detection
    context_str = f"\nContext: {sample_context}\n" if sample_context else ""
    
    question = (
        f"You are analyzing a categorical column from a dataset.{context_str}\n"
        f"Column name: '{column_name}'\n"
        f"Category values: {category_values}\n\n"
        "Determine if these categories have a NATURAL ORDERING (ordinal relationship).\n\n"
        "Examples of ORDINAL categories:\n"
        "  - ['low', 'medium', 'high'] → ordered by magnitude\n"
        "  - ['poor', 'fair', 'good', 'excellent'] → ordered by quality\n"
        "  - ['freshman', 'sophomore', 'junior', 'senior'] → ordered by progression\n"
        "  - ['A11', 'A12', 'A13', 'A14'] → likely ordered codes (check meaning)\n"
        "  - ['< 0 years', '0-1 years', '1-4 years', '4-7 years', '7+ years'] → time ranges\n\n"
        "Examples of NON-ORDINAL (nominal) categories:\n"
        "  - ['red', 'blue', 'green'] → no inherent order\n"
        "  - ['USA', 'Canada', 'UK'] → no inherent order\n"
        "  - ['checking', 'savings', 'money_market'] → no inherent order\n\n"
        "If ordinal, provide the values in ASCENDING order (lowest/worst to highest/best).\n"
        "If the column name suggests a domain (like 'credit_history' or 'employment_status'), "
        "use domain knowledge to determine the correct ordering.\n\n"
        "Return ONLY a valid JSON object with keys:\n"
        "  - is_ordinal: boolean\n"
        "  - ordered_values: array of strings in ascending order (empty if not ordinal)\n"
        "  - confidence: number 0.0-1.0\n"
        "  - reasoning: brief explanation string\n"
        "  - order_type: 'ascending' | 'descending' | 'custom' | null"
    )
    
    payload = {
        "columns": category_values,  # Using category values as "columns" for API compatibility
        "question": question
    }
    
    logger.info(f"🤖 Detecting ordinal structure for '{column_name}' ({len(category_values)} categories)")
    logger.debug(f"   Ordinal API request: url={api_url}")
    logger.debug(f"   Ordinal API payload: {json.dumps(payload, indent=2)}")
    
    # Retry logic: up to 60 seconds with exponential backoff
    max_retry_time = 60.0
    retry_start = time.time()
    attempt = 0
    base_delay = 1.0  # Start with 1 second delay
    last_error = None
    last_status_code = None
    last_response_text = None
    
    while (time.time() - retry_start) < max_retry_time:
        attempt += 1
        try:
            request_start = time.time()
            response = requests.post(api_url, json=payload, timeout=10)
            elapsed = time.time() - request_start
            
            if response.status_code == 200:
                raw_result = response.json()
                logger.debug(f"   Ordinal API raw response: {json.dumps(raw_result, indent=2)}")
                
                # Transform API response to our expected format
                # API may return 'primary_answer' instead of 'is_ordinal'
                if 'is_ordinal' in raw_result:
                    is_ordinal = raw_result['is_ordinal']
                elif 'primary_answer' in raw_result:
                    # Convert string 'true'/'false' to boolean
                    primary = raw_result['primary_answer']
                    is_ordinal = primary.lower() == 'true' if isinstance(primary, str) else bool(primary)
                else:
                    is_ordinal = False
                
                # Extract ordered values from API response
                # Use `or []` to handle explicit null values in JSON response
                ordered_values = raw_result.get('ordered_values') or []
                if not ordered_values and is_ordinal:
                    # Try to parse from suggestions or other fields
                    ordered_values = raw_result.get('suggestions') or []
                
                # CRITICAL: If is_ordinal=True but ordered_values is empty, disable ordinal
                # This prevents downstream crashes in SetEncoder
                if is_ordinal and not ordered_values:
                    logger.warning(f"⚠️  Ordinal API returned is_ordinal=True but no ordered_values for '{column_name}' - disabling ordinal")
                    is_ordinal = False
                
                # Build normalized result
                result = {
                    'is_ordinal': is_ordinal,
                    'ordered_values': ordered_values if is_ordinal else [],
                    'confidence': raw_result.get('confidence', 1.0 if is_ordinal else 0.0),
                    'reasoning': raw_result.get('reasoning', ''),
                    'order_type': raw_result.get('order_type', 'ascending' if is_ordinal else None)
                }
                
                if attempt > 1:
                    logger.info(f"   ✅ Ordinal detection (attempt {attempt}): is_ordinal={is_ordinal}, confidence={result['confidence']:.2f} ({elapsed:.2f}s)")
                else:
                    logger.info(f"   ✅ Ordinal detection: is_ordinal={is_ordinal}, confidence={result['confidence']:.2f} ({elapsed:.2f}s)")
                
                # Cache the normalized result
                cache.set(column_name, category_values, result)
                
                return result
            else:
                # Non-200 response - retry
                last_status_code = response.status_code
                last_response_text = response.text if response.text else "(empty)"
                last_error = f"HTTP {response.status_code}"
                
                remaining = max_retry_time - (time.time() - retry_start)
                if remaining > base_delay:
                    logger.warning(
                        f"⚠️  Ordinal API returned {response.status_code} (attempt {attempt}), retrying in {base_delay:.1f}s...\n"
                        f"   URL: {api_url}\n"
                        f"   Request: {json.dumps(payload)}\n"
                        f"   Response: {last_response_text}"
                    )
                    time.sleep(base_delay)
                    base_delay = min(base_delay * 2, 10.0)  # Exponential backoff, max 10s
                else:
                    break  # No time left for retry
                    
        except requests.exceptions.Timeout:
            last_error = "timeout (10s)"
            remaining = max_retry_time - (time.time() - retry_start)
            if remaining > base_delay:
                logger.warning(
                    f"⚠️  Ordinal API timeout (attempt {attempt}), retrying in {base_delay:.1f}s...\n"
                    f"   URL: {api_url}\n"
                    f"   Request: {json.dumps(payload)}"
                )
                time.sleep(base_delay)
                base_delay = min(base_delay * 2, 10.0)
            else:
                break
                
        except requests.exceptions.ConnectionError as e:
            last_error = f"connection error: {e}"
            remaining = max_retry_time - (time.time() - retry_start)
            if remaining > base_delay:
                logger.warning(
                    f"⚠️  Ordinal API connection error (attempt {attempt}), retrying in {base_delay:.1f}s...\n"
                    f"   URL: {api_url}\n"
                    f"   Request: {json.dumps(payload)}\n"
                    f"   Error: {e}"
                )
                time.sleep(base_delay)
                base_delay = min(base_delay * 2, 10.0)
            else:
                break
                
        except Exception as e:
            last_error = f"unexpected error: {e}"
            remaining = max_retry_time - (time.time() - retry_start)
            if remaining > base_delay:
                logger.warning(
                    f"⚠️  Ordinal API failed (attempt {attempt}), retrying in {base_delay:.1f}s...\n"
                    f"   URL: {api_url}\n"
                    f"   Request: {json.dumps(payload)}\n"
                    f"   Error: {e}"
                )
                time.sleep(base_delay)
                base_delay = min(base_delay * 2, 10.0)
            else:
                break
    
    # All retries exhausted - log comprehensive error info and use fallback
    total_time = time.time() - retry_start
    error_details = [
        f"⚠️  Ordinal API failed after {attempt} attempts ({total_time:.1f}s), using fallback",
        f"   URL: {api_url}",
        f"   Column: '{column_name}'",
        f"   Categories: {category_values}",
        f"   Last error: {last_error}",
    ]
    if last_status_code:
        error_details.append(f"   Last status code: {last_status_code}")
    if last_response_text:
        error_details.append(f"   Last response body: {last_response_text}")
    error_details.append(f"   Request payload:\n{json.dumps(payload, indent=4)}")
    
    logger.warning("\n".join(error_details))
    return _fallback_ordinal_detection(column_name, category_values)


def _fallback_ordinal_detection(column_name: str, category_values: List[str]) -> Dict[str, Any]:
    """
    Pattern-based fallback for ordinal detection when LLM is unavailable.
    
    Detects common ordinal patterns without LLM.
    """
    # Common ordinal patterns (case-insensitive matching)
    ordinal_patterns = {
        # Magnitude patterns
        ("low", "medium", "high"): ["low", "medium", "high"],
        ("low", "med", "high"): ["low", "med", "high"],
        ("small", "medium", "large"): ["small", "medium", "large"],
        ("xs", "s", "m", "l", "xl"): ["xs", "s", "m", "l", "xl"],
        ("xs", "s", "m", "l", "xl", "xxl"): ["xs", "s", "m", "l", "xl", "xxl"],
        
        # Quality patterns  
        ("poor", "fair", "good", "excellent"): ["poor", "fair", "good", "excellent"],
        ("bad", "ok", "good", "great"): ["bad", "ok", "good", "great"],
        ("poor", "fair", "good"): ["poor", "fair", "good"],
        ("critical", "high", "moderate", "low"): ["low", "moderate", "high", "critical"],
        
        # Education patterns
        ("freshman", "sophomore", "junior", "senior"): ["freshman", "sophomore", "junior", "senior"],
        ("undergraduate", "graduate", "postgraduate"): ["undergraduate", "graduate", "postgraduate"],
        
        # Agreement/satisfaction
        ("strongly_disagree", "disagree", "neutral", "agree", "strongly_agree"): 
            ["strongly_disagree", "disagree", "neutral", "agree", "strongly_agree"],
        ("very_unsatisfied", "unsatisfied", "neutral", "satisfied", "very_satisfied"):
            ["very_unsatisfied", "unsatisfied", "neutral", "satisfied", "very_satisfied"],
        
        # Frequency
        ("never", "rarely", "sometimes", "often", "always"): 
            ["never", "rarely", "sometimes", "often", "always"],
        ("none", "few", "some", "many", "all"): ["none", "few", "some", "many", "all"],
    }
    
    # Normalize values for matching
    normalized_values = tuple(sorted([v.lower().replace(" ", "_").replace("-", "_") for v in category_values]))
    
    for pattern, ordered in ordinal_patterns.items():
        normalized_pattern = tuple(sorted([p.lower().replace(" ", "_").replace("-", "_") for p in pattern]))
        if normalized_values == normalized_pattern:
            # Map back to original case
            value_map = {v.lower().replace(" ", "_").replace("-", "_"): v for v in category_values}
            ordered_original = [value_map.get(o.lower().replace(" ", "_").replace("-", "_"), o) for o in ordered]
            return {
                "is_ordinal": True,
                "ordered_values": ordered_original,
                "confidence": 0.9,
                "reasoning": "Matched known ordinal pattern",
                "order_type": "ascending"
            }
    
    # Check for numeric-like codes (A1, A2, A3... or 1, 2, 3...)
    try:
        # Try numeric sorting
        sorted_numeric = sorted(category_values, key=lambda x: float(x))
        if sorted_numeric != category_values:
            return {
                "is_ordinal": True,
                "ordered_values": sorted_numeric,
                "confidence": 0.8,
                "reasoning": "Numeric values detected, assumed ordinal",
                "order_type": "ascending"
            }
    except (ValueError, TypeError):
        pass
    
    # Check for alphanumeric codes like A11, A12, A13, A14
    import re
    code_pattern = re.compile(r'^([A-Za-z]*)(\d+)$')
    code_matches = [(code_pattern.match(v), v) for v in category_values]
    
    if all(match for match, _ in code_matches):
        # All values match alphanumeric code pattern
        prefixes = set(match.group(1) for match, _ in code_matches)
        if len(prefixes) == 1:
            # Same prefix, sort by number
            sorted_codes = sorted(category_values, key=lambda v: int(code_pattern.match(v).group(2)))
            return {
                "is_ordinal": True,
                "ordered_values": sorted_codes,
                "confidence": 0.7,
                "reasoning": f"Alphanumeric codes with same prefix (likely ordinal)",
                "order_type": "ascending"
            }
    
    # Default: not ordinal
    return {
        "is_ordinal": False,
        "ordered_values": [],
        "confidence": 0.5,
        "reasoning": "No ordinal pattern detected (using fallback heuristics)",
        "order_type": None
    }


def detect_ordinal_categories_batch(
    columns_with_values: Dict[str, List[str]],
    sample_context: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Batch version of detect_ordinal_categories for multiple columns.
    
    Calls LLM once with all columns to reduce API calls.
    
    Args:
        columns_with_values: Dict mapping column names to their category values
            e.g., {"credit_rating": ["poor", "fair", "good"], "status": ["active", "inactive"]}
        sample_context: Optional context about the data
    
    Returns:
        Dict mapping column names to ordinal detection results
    """
    results = {}
    cache = _get_ordinal_cache()
    
    # Check cache for all columns first, validating each cached result
    uncached_columns = {}
    for col_name, values in columns_with_values.items():
        cached = cache.get(col_name, values)
        if cached:
            # Validate cached result - reject if it contains an error or is malformed
            has_error = 'error' in cached
            is_ordinal = cached.get('is_ordinal', False)
            ordered_values = cached.get('ordered_values')
            
            if has_error:
                # Cached result contains HTTP error response - delete and retry
                logger.warning(f"⚠️  Cached result for '{col_name}' contains error, deleting and retrying")
                cache.delete(col_name, values)
                uncached_columns[col_name] = values
            elif is_ordinal and not ordered_values:
                logger.warning(f"⚠️  Bad cached result for '{col_name}' (is_ordinal=True but no ordered_values), deleting")
                cache.delete(col_name, values)
                uncached_columns[col_name] = values
            else:
                results[col_name] = cached
        else:
            uncached_columns[col_name] = values
    
    if not uncached_columns:
        logger.info(f"✅ All {len(columns_with_values)} columns found in ordinal cache")
        return results
    
    logger.info(f"🤖 Batch ordinal detection: {len(uncached_columns)} uncached, {len(results)} cached")
    
    # For now, call individually (could optimize with batch API later)
    for col_name, values in uncached_columns.items():
        result = detect_ordinal_categories(col_name, values, sample_context)
        results[col_name] = result
    
    return results


def detect_hybrid_columns(columns: List[str], col_types: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Ask LLM to detect hybrid column groups in a schema.
    
    Args:
        columns: List of column names to analyze
        col_types: Optional dict of column types (for context)
    
    Returns:
        Dict with 'groups' array containing detected hybrid groups
        Each group has: type, columns, prefix, confidence, reasoning
    
    Example:
        >>> result = detect_hybrid_columns(["shipping_addr", "shipping_city", "shipping_state"])
        >>> groups = result.get('groups', [])
        >>> print(f"Found {len(groups)} hybrid groups")
    """
    try:
        import requests
    except ImportError:
        logger.error("requests library not available - cannot call cache.featrix.com API")
        return {"groups": []}
    
    api_url = "https://cache.featrix.com/query-schema"
    
    # Build detailed prompt
    question = (
        "You are given the column names of a tabular dataset. "
        "Analyze the columns and identify SMALL GROUPS of semantically related columns "
        "that should be encoded or modeled together (i.e., they describe different aspects "
        "of the same underlying thing).\n\n"
        "Specifically look for (but do not limit yourself to):\n"
        "  1) Address components (e.g. street, city, state, zip, country)\n"
        "  2) Coordinate pairs or sets (e.g. latitude/longitude)\n"
        "  3) Entity attributes (e.g. customer_name, customer_id, customer_type, account_status)\n"
        "  4) Temporal ranges or pairs (e.g. start_date, end_date; created_at, updated_at)\n\n"
        "Rules:\n"
        "  - Only group columns that clearly refer to the SAME entity/concept.\n"
        "  - Each group must have at least 2 columns.\n"
        "  - Do NOT invent new column names; use only the ones provided.\n"
        "  - 'type' should be one of: 'address', 'coordinates', 'entity_attributes', "
        "'temporal_range', or 'other'.\n"
        "  - 'prefix' should be a short, descriptive base name for the group "
        "(often the shared prefix of the columns, if meaningful).\n"
        "  - 'confidence' is a number from 0.0 to 1.0.\n"
        "  - 'reasoning' should be a short sentence explaining why these columns belong together.\n\n"
        "Return ONLY a valid JSON object with a single key 'groups', where 'groups' is an array. "
        "Each group must be an object with keys: type, columns (list of strings), prefix, "
        "confidence, reasoning."
    )
    
    payload = {
        "columns": columns,
        "question": question
    }
    
    logger.info(f"🤖 Calling cache.featrix.com for hybrid column detection ({len(columns)} columns)")
    logger.info(f"   API endpoint: {api_url}")
    logger.info(f"   Timeout: 10s (reduced from 30s for faster failure detection)")
    logger.info(f"   Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        import time
        start_time = time.time()
        logger.info(f"   📡 Sending POST request now...")
        response = requests.post(api_url, json=payload, timeout=10)
        elapsed = time.time() - start_time
        
        logger.info(f"   ✅ Request completed in {elapsed:.2f}s")
        logger.info(f"   API response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            num_groups = len(result.get('groups', []))
            logger.info(f"✅ LLM analysis complete: found {num_groups} hybrid groups")
            return result
        else:
            logger.warning(f"⚠️  API returned {response.status_code}: {response.text[:200]}")
            logger.warning(f"   Falling back to pattern-based detection only")
            return {"groups": []}
            
    except requests.exceptions.Timeout:
        logger.warning("⚠️  API request timeout (10s) - service may be down")
        logger.warning("   Falling back to pattern-based detection only")
        return {"groups": []}
        
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"⚠️  API connection error: {e}")
        return {"groups": []}
        
    except Exception as e:
        logger.warning(f"⚠️  API call failed: {e}")
        return {"groups": []}


def suggest_target_columns(columns: List[str], col_types: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Ask LLM to suggest which columns would be good targets for a prediction model.
    
    Uses caching to avoid re-querying the same column sets.
    
    Args:
        columns: List of column names to analyze
        col_types: Optional dict of column types (for context)
    
    Returns:
        Dict with 'targets' array containing suggested target columns
        Each target has: column_name, confidence, reasoning, target_type (set/scalar)
    
    Example:
        >>> result = suggest_target_columns(["revenue", "customer_id", "churn", "age"])
        >>> targets = result.get('targets', [])
        >>> best_target = targets[0]['column_name'] if targets else None
    """
    # Check cache first
    cache = _get_target_cache()
    cached_result = cache.get(columns)
    if cached_result:
        # Validate cached result - reject if it contains an error
        if 'error' in cached_result:
            logger.warning(f"⚠️  Cached target suggestions contain error, deleting and retrying: {cached_result.get('error', 'unknown')[:100]}")
            cache.delete(columns)
            # Don't return - fall through to recompute
        else:
            return cached_result
    
    try:
        import requests
    except ImportError:
        logger.error("requests library not available - cannot call cache.featrix.com API")
        return {"targets": []}
    
    api_url = "https://cache.featrix.com/query-schema"
    
    # Build prompt for target column suggestion
    question = (
        "You are given the column names of a tabular dataset. "
        "Your task is to identify which columns would be GOOD TARGETS for a prediction model.\n\n"
        "A good target column is typically:\n"
        "  1) A categorical outcome (e.g., 'churn', 'fraud', 'approved', 'status')\n"
        "  2) A numeric value to predict (e.g., 'revenue', 'price', 'score', 'rating')\n"
        "  3) A classification label (e.g., 'category', 'type', 'class')\n"
        "  4) A binary outcome (e.g., 'is_fraud', 'has_disease', 'purchased')\n\n"
        "NOT good targets (exclude these):\n"
        "  - ID columns (e.g., 'id', 'customer_id', 'order_id', 'uuid')\n"
        "  - Timestamps/dates (e.g., 'created_at', 'updated_at', 'timestamp')\n"
        "  - Index/row identifiers (e.g., 'index', 'row_id', 'row_number')\n"
        "  - Input features (e.g., 'age', 'name', 'address', 'description')\n\n"
        "Rules:\n"
        "  - Return ONLY columns from the provided list (do not invent new names).\n"
        "  - Rank targets by how suitable they are for prediction (best first).\n"
        "  - 'target_type' should be 'set' for categorical/classification targets, 'scalar' for numeric targets.\n"
        "  - 'confidence' is a number from 0.0 to 1.0 indicating how confident you are this is a good target.\n"
        "  - 'reasoning' should explain why this column is a good prediction target.\n\n"
        "Return ONLY a valid JSON object with a single key 'targets', where 'targets' is an array. "
        "Each target must be an object with keys: column_name, confidence, reasoning, target_type."
    )
    
    payload = {
        "columns": columns,
        "question": question
    }
    
    logger.info(f"🤖 Calling cache.featrix.com for target column suggestions ({len(columns)} columns)")
    logger.info(f"   API endpoint: {api_url}")
    logger.info(f"   Timeout: 10s")
    
    try:
        import time
        start_time = time.time()
        response = requests.post(api_url, json=payload, timeout=10)
        elapsed = time.time() - start_time
        
        logger.info(f"   ✅ Request completed in {elapsed:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            num_targets = len(result.get('targets', []))
            logger.info(f"✅ LLM analysis complete: found {num_targets} suggested target columns")
            
            # Cache the result
            cache.set(columns, result)
            
            return result
        else:
            logger.warning(f"⚠️  API returned {response.status_code}: {response.text[:200]}")
            return {"targets": []}
            
    except requests.exceptions.Timeout:
        logger.warning("⚠️  API request timeout (10s) - service may be down")
        return {"targets": []}
        
    except requests.exceptions.ConnectionError as e:
        logger.warning(f"⚠️  API connection error: {e}")
        return {"targets": []}
        
    except Exception as e:
        logger.warning(f"⚠️  API call failed: {e}")
        return {"targets": []}


def test_api():
    """Test the API with sample data."""
    test_columns = [
        "shipping_address",
        "shipping_city", 
        "shipping_state",
        "shipping_zip",
        "warehouse_latitude",
        "warehouse_longitude",
        "customer_name",
        "customer_id",
        "customer_type",
        "order_start_date",
        "order_end_date",
        "revenue",
        "quantity",
        "status"
    ]
    
    print("Testing cache.featrix.com API...")
    result = detect_hybrid_columns(test_columns)
    
    print(json.dumps(result, indent=2))
    print(f"\nDetected {len(result.get('groups', []))} groups")


if __name__ == "__main__":
    # Enable logging for standalone test
    logging.basicConfig(level=logging.INFO)
    test_api()

