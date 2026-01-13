"""
Vector query optimizer for IRIS HNSW compatibility

Transforms parameterized vector queries into literal form to enable HNSW index optimization.
This is a server-side workaround for IRIS's requirement that vectors in ORDER BY clauses
must be literals, not parameters.
"""

import base64
import binascii
import logging
import re
import struct
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class OptimizationMetrics:
    """Performance metrics for vector query optimization"""

    transformation_time_ms: float
    vector_params_found: int
    vector_params_transformed: int
    sql_length_before: int
    sql_length_after: int
    params_count_before: int
    params_count_after: int
    constitutional_sla_compliant: bool
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for logging"""
        return {
            "transformation_time_ms": round(self.transformation_time_ms, 2),
            "vector_params_found": self.vector_params_found,
            "vector_params_transformed": self.vector_params_transformed,
            "sql_length_before": self.sql_length_before,
            "sql_length_after": self.sql_length_after,
            "params_count_before": self.params_count_before,
            "params_count_after": self.params_count_after,
            "constitutional_sla_compliant": self.constitutional_sla_compliant,
            "sla_threshold_ms": 5.0,
        }


class VectorQueryOptimizer:
    """
    Optimizes vector queries for IRIS HNSW performance by converting
    parameterized TO_VECTOR() calls in ORDER BY clauses to literal form.
    """

    # Constitutional SLA requirement: 5ms maximum transformation time
    CONSTITUTIONAL_SLA_MS = 5.0

    def __init__(self):
        self.enabled = True
        self.metrics_history: list[OptimizationMetrics] = []
        self.sla_violations = 0
        self.total_optimizations = 0

    def optimize_query(self, sql: str, params: list | None = None) -> tuple[str, list | None]:
        """
        Transform parameterized vector queries into literal form for HNSW optimization.
        """
        start_time = time.perf_counter()

        sql_length_before = len(sql) if sql else 0
        params_count_before = len(params) if params else 0

        if sql is None:
            return "", params

        if not isinstance(sql, str):
            return str(sql), params

        logger.info(
            "🚀 optimize_query CALLED",
            enabled=self.enabled,
            sql_preview=sql[:150],
            params_count=len(params) if params else 0,
        )

        if not self.enabled:
            return sql, params

        # STEP 0: Strip trailing semicolons
        sql = sql.rstrip(";").strip()

        sql_upper = sql.upper()

        # STEP 1: Handle HNSW Index Creation (DDL)
        if "CREATE" in sql_upper and "INDEX" in sql_upper and "HNSW" in sql_upper:
            optimized_sql = self._rewrite_hnsw_create_index(sql)
            if optimized_sql != sql:
                logger.info("HNSW DDL successfully rewritten", sql=optimized_sql[:150])
                return optimized_sql, params

        # Skip other DDL
        ddl_keywords = ["CREATE TABLE", "DROP TABLE", "ALTER TABLE", "CREATE INDEX", "DROP INDEX"]
        if any(keyword in sql_upper for keyword in ddl_keywords):
            return sql, params

        # STEP 2: Convert PostgreSQL LIMIT to IRIS TOP
        sql = self._convert_limit_to_top(sql)

        # STEP 3: Rewrite pgvector operators to IRIS vector functions
        sql = self._rewrite_pgvector_operators(sql)

        # Handle INSERT/UPDATE
        has_vector_pattern = "TO_VECTOR" in sql_upper or re.search(r"'\[[\d.,\s\-eE]+\]'", sql)
        if ("INSERT" in sql_upper or "UPDATE" in sql_upper) and has_vector_pattern:
            optimized_sql = self._optimize_insert_vectors(sql, start_time)
            optimized_sql = self._fix_order_by_aliases(optimized_sql)
            return optimized_sql, params

        if "ORDER BY" not in sql_upper or "TO_VECTOR" not in sql_upper:
            return sql, params

        if not params:
            return self._optimize_literal_vectors(sql, start_time)

        # Parameterized ORDER BY optimization
        order_by_pattern = re.compile(
            r"(VECTOR_(?:COSINE|DOT_PRODUCT|L2))\s*\(\s*"
            r"(\w+)\s*,\s*"
            r"(TO_VECTOR\s*\(\s*([?%]s?)\s*(?:,\s*(\w+))?\s*\))",
            re.IGNORECASE,
        )

        matches = list(order_by_pattern.finditer(sql))
        if not matches:
            return sql, params

        optimized_sql = sql
        params_used = []
        remaining_params = list(params) if params else []

        for match in reversed(matches):
            data_type = match.group(5) or "FLOAT"
            param_index = sql[: match.start()].count("?") + sql[: match.start()].count("%s")

            if param_index >= len(remaining_params):
                continue

            vector_param = remaining_params[param_index]
            vector_literal = self._convert_vector_to_literal(vector_param)

            if vector_literal is None:
                continue

            MAX_LITERAL_SIZE_BYTES = 3000
            if len(vector_literal) > MAX_LITERAL_SIZE_BYTES:
                remaining_params[param_index] = vector_literal
                continue

            new_to_vector = f"TO_VECTOR('{vector_literal}', {data_type})"
            to_vector_start = match.start(3)
            to_vector_end = match.end(3)
            optimized_sql = (
                optimized_sql[:to_vector_start] + new_to_vector + optimized_sql[to_vector_end:]
            )
            params_used.append(param_index)

        for idx in sorted(params_used, reverse=True):
            remaining_params.pop(idx)

        transformation_time_ms = (time.perf_counter() - start_time) * 1000
        self._record_metrics(
            OptimizationMetrics(
                transformation_time_ms=transformation_time_ms,
                vector_params_found=len(matches),
                vector_params_transformed=len(params_used),
                sql_length_before=sql_length_before,
                sql_length_after=len(optimized_sql),
                params_count_before=params_count_before,
                params_count_after=len(remaining_params),
                constitutional_sla_compliant=(transformation_time_ms <= self.CONSTITUTIONAL_SLA_MS),
            )
        )

        optimized_sql = self._fix_order_by_aliases(optimized_sql)
        return optimized_sql, remaining_params if remaining_params else None

    def _rewrite_hnsw_create_index(self, sql: str) -> str:
        """
        Translate PostgreSQL 'CREATE INDEX ... USING hnsw' to IRIS '... AS HNSW'
        """
        pattern = re.compile(
            r"CREATE\s+(UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\".]+)\s+ON\s+([\w\".]+)\s+USING\s+hnsw\s*\(\s*([^)]+)\s*\)",
            re.IGNORECASE,
        )

        def replace_hnsw(match):
            is_unique = match.group(1) or ""
            idx_name = match.group(2)
            table_name = match.group(3)
            col_def = match.group(4).strip()

            parts = col_def.split()
            if not parts:
                return match.group(0)

            col_name = parts[0]
            ops = " ".join(parts[1:]).lower() if len(parts) > 1 else ""

            if "cosine" in ops:
                distance = "Cosine"
            elif "ip" in ops or "dot" in ops:
                distance = "DotProduct"
            elif "l2" in ops:
                raise NotImplementedError("L2 distance is not supported by IRIS HNSW indexes.")
            else:
                distance = "Cosine"

            clean_col = col_name.replace('"', "")
            return f"CREATE {is_unique}INDEX {idx_name} ON {table_name}({clean_col}) AS HNSW(Distance='{distance}')"

        return pattern.sub(replace_hnsw, sql)

    def _rewrite_pgvector_operators(self, sql: str) -> str:
        """
        Rewrite pgvector operators to IRIS vector functions.
        """
        if not sql:
            return sql
        return self._rewrite_operators_in_text(sql)

    def _rewrite_operators_in_text(self, sql: str) -> str:
        pattern_cosine = r"([\w\.]+|'[^']*'|\[[^\]]*\])\s*<=>\s*('[^']*'|\[[^\]]*\]|\?|%s|\$\d+)"

        def replace_cosine(match):
            left, right = match.groups()
            is_param = right in ("?", "%s") or right.startswith("$")
            if "TO_VECTOR" in left.upper() or "TO_VECTOR" in right.upper():
                return f"VECTOR_COSINE({left}, {right})"
            if is_param:
                return f"VECTOR_COSINE({left}, TO_VECTOR({right}, DOUBLE))"
            if left.startswith("'") or left.startswith("["):
                opt_left = self._optimize_vector_literal(left)
                opt_right = self._optimize_vector_literal(right)
                return f"VECTOR_COSINE(TO_VECTOR('{opt_left}', DOUBLE), TO_VECTOR('{opt_right}', DOUBLE))"
            opt_right = self._optimize_vector_literal(right)
            wrapped = f"TO_VECTOR('{opt_right}', DOUBLE)"
            return (
                f"VECTOR_COSINE({left}, {wrapped})"
                if len(wrapped) <= 3000
                else f"VECTOR_COSINE({left}, '{opt_right}')"
            )

        sql = re.sub(pattern_cosine, replace_cosine, sql)

        if "<->" in sql:
            raise NotImplementedError("L2 distance operator (<->) is not supported by IRIS.")

        pattern_ip = r"([\w\.]+|'[^']*'|\[[^\]]*\])\s*<#>\s*('[^']*'|\[[^\]]*\]|\?|%s|\$\d+)"

        def replace_ip(match):
            left, right = match.groups()
            is_param = right in ("?", "%s") or right.startswith("$")
            if "TO_VECTOR" in left.upper() or "TO_VECTOR" in right.upper():
                return f"(-VECTOR_DOT_PRODUCT({left}, {right}))"
            if is_param:
                return f"(-VECTOR_DOT_PRODUCT({left}, TO_VECTOR({right}, DOUBLE)))"
            if left.startswith("'") or left.startswith("["):
                opt_left = self._optimize_vector_literal(left)
                opt_right = self._optimize_vector_literal(right)
                return f"(-VECTOR_DOT_PRODUCT(TO_VECTOR('{opt_left}', DOUBLE), TO_VECTOR('{opt_right}', DOUBLE)))"
            opt_right = self._optimize_vector_literal(right)
            wrapped = f"TO_VECTOR('{opt_right}', DOUBLE)"
            return (
                f"(-VECTOR_DOT_PRODUCT({left}, {wrapped}))"
                if len(wrapped) <= 3000
                else f"(-VECTOR_DOT_PRODUCT({left}, '{opt_right}'))"
            )

        return re.sub(pattern_ip, replace_ip, sql)

    def _optimize_vector_literal(self, literal: str) -> str:
        clean = literal.strip("'\"")
        if clean.startswith("[") and clean.endswith("]"):
            clean = clean[1:-1]
        return clean

    def _convert_limit_to_top(self, sql: str) -> str:
        limit_pattern = re.compile(r"\s+LIMIT\s+(\d+)(?:\s+OFFSET\s+(\d+))?\s*(;?)$", re.IGNORECASE)
        match = limit_pattern.search(sql)
        if not match:
            return sql
        limit_val = match.group(1)
        sql_without_limit = sql[: match.start()] + match.group(3)
        select_pattern = re.compile(r"(SELECT\s+(?:DISTINCT\s+)?)", re.IGNORECASE)
        return select_pattern.sub(
            lambda m: f"{m.group(1)}TOP {limit_val} ", sql_without_limit, count=1
        )

    def _fix_order_by_aliases(self, sql: str) -> str:
        return sql

    def bind_vector_parameter(self, vector: list[float], data_type: str = "DECIMAL") -> str:
        if not vector:
            raise ValueError("Vector empty")
        vector_json = "[" + ",".join(str(float(v)) for v in vector) + "]"
        return f"TO_VECTOR('{vector_json}', {data_type.upper()})"

    def _convert_vector_to_literal(self, vector_param: str) -> str | None:
        if not isinstance(vector_param, str) or not vector_param:
            return None
        if vector_param.startswith("[") and vector_param.endswith("]"):
            return vector_param
        if vector_param.startswith("base64:"):
            binary_data = b""
            try:
                b64_data = vector_param[7:]
                if not b64_data:
                    return None
                binary_data = base64.b64decode(b64_data)
                num_floats = len(binary_data) // 4
                if num_floats == 0:
                    return None
                floats = struct.unpack(f"{num_floats}f", binary_data)
                return ",".join(str(float(v)) for v in floats)
            except (binascii.Error, struct.error):
                return None
        return vector_param if "," in vector_param else None

    def _optimize_insert_vectors(self, sql: str, start_time: float) -> str:
        return re.sub(
            r"(TO_VECTOR\s*\(\s*)?'(\[[^']+\])'",
            lambda m: m.group(0) if m.group(1) else f"TO_VECTOR('{m.group(2)}', DOUBLE)",
            sql,
            flags=re.IGNORECASE,
        )

    def _optimize_literal_vectors(self, sql: str, start_time: float) -> tuple[str, list | None]:
        pattern = re.compile(
            r"TO_VECTOR\s*\(\s*'(base64:[^']+|\[[0-9.,\s-]+\]|[0-9.,\s-]+)'(?:\s*,\s*(\w+))?\s*\)",
            re.IGNORECASE,
        )
        matches = list(pattern.finditer(sql))
        if not matches:
            return sql, None
        optimized_sql = sql
        for match in reversed(matches):
            converted = self._convert_vector_to_literal(match.group(1))
            if converted:
                new_call = f"TO_VECTOR('{converted}', {match.group(2) or 'FLOAT'})"
                optimized_sql = (
                    optimized_sql[: match.start()] + new_call + optimized_sql[match.end() :]
                )
        return optimized_sql, None

    def _record_metrics(self, metrics: OptimizationMetrics):
        self.total_optimizations += 1
        if not metrics.constitutional_sla_compliant:
            self.sla_violations += 1
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)

    def get_performance_stats(self) -> dict[str, Any]:
        if not self.metrics_history:
            return {"total_optimizations": 0, "sla_violations": 0, "sla_compliance_rate": 100.0}
        recent_times = [m.transformation_time_ms for m in self.metrics_history[-50:]]
        return {
            "total_optimizations": self.total_optimizations,
            "sla_violations": self.sla_violations,
            "sla_compliance_rate": round(
                (self.total_optimizations - self.sla_violations) / self.total_optimizations * 100, 2
            ),
            "avg_transformation_time_ms": round(sum(recent_times) / len(recent_times), 2),
            "constitutional_sla_ms": self.CONSTITUTIONAL_SLA_MS,
        }


_optimizer = VectorQueryOptimizer()


def optimize_vector_query(sql: str, params: list | None = None) -> tuple[str, list | None]:
    return _optimizer.optimize_query(sql, params)


def enable_optimization(enabled: bool = True):
    _optimizer.enabled = enabled


def get_performance_stats() -> dict[str, Any]:
    return _optimizer.get_performance_stats()


def get_sla_compliance_report() -> str:
    stats = get_performance_stats()
    return f"Total: {stats['total_optimizations']}, Rate: {stats.get('sla_compliance_rate', 100)}%"
