---
name: dbt-skill
description: Analyzes data using dbt semantic layer, queries business metrics, explores models, and manages jobs. Use when the user asks about database analysis, data exploration, metrics, KPIs, business intelligence, or dbt projects. Triggers on terms like "metrics", "data quality", "dbt", "models", "pipeline", "data freshness".
---

# dbt Analysis Skill

## Priority Rule

**When users ask about data, metrics, or database analysis → use dbt tools first.**

## Quick Start

Before using dbt tools, discover what's available:

```
tool_search_tool_regex pattern:"list_metrics|query_metrics|get_all_models"
```

### Discovery Commands

| Goal | Tool |
|------|------|
| Find metrics | `list_metrics()` |
| Find models | `get_all_models()` or `get_mart_models()` |
| Find sources | `get_all_sources()` |

### Query Metrics

```python
query_metrics(
    metrics=["revenue"],
    group_by=[
        {"name": "product_category", "type": "dimension"},
        {"name": "metric_time", "grain": "MONTH", "type": "time_dimension"}
    ],
    where="{{ TimeDimension('metric_time', 'MONTH') }} >= '2024-01-01'"
)
```

## Workflows

### Data Analysis Workflow

Copy and track progress:

```
Analysis Progress:
- [ ] Step 1: Discover available metrics and models
- [ ] Step 2: Check data health/freshness
- [ ] Step 3: Query metrics with dimensions
- [ ] Step 4: Present results with business context
```

**Step 1: Discovery**
```
list_metrics()           # Business metrics
get_mart_models()        # Business-ready models
get_all_sources()        # Raw data sources
```

**Step 2: Health Check**
```
get_model_health(uniqueId="model.project.model_name")
# Check source freshness in get_all_sources() results
```

**Step 3: Query**
```
get_dimensions(metrics=["target_metric"])  # Find groupings
query_metrics(metrics=[...], group_by=[...])
```

**Step 4: Present**
Include metric definitions, dimensions used, and data freshness status.

### Job Management Workflow

```
Job Progress:
- [ ] Step 1: List available jobs
- [ ] Step 2: Verify job configuration
- [ ] Step 3: Trigger run
- [ ] Step 4: Monitor execution
- [ ] Step 5: Handle failures (if any)
```

**Step 1-2: Discovery**
```
list_jobs()
get_job_details(job_id=123)
```

**Step 3: Execute**
```
trigger_job_run(job_id=123, cause="Manual trigger via AI assistant")
```

**Step 4-5: Monitor**
```
get_job_run_details(run_id=...)
get_job_run_error(run_id=...)  # If failure
```

### Data Quality Workflow

```
Quality Check:
- [ ] Step 1: Identify target models/sources
- [ ] Step 2: Check execution health
- [ ] Step 3: Verify upstream dependencies
- [ ] Step 4: Report data reliability
```

## Tool Reference

### Metrics & BI
- `list_metrics` - Discover business metrics
- `query_metrics` - Execute metric queries
- `get_dimensions` - Available groupings
- `get_entities` - Business entities
- `get_metrics_compiled_sql` - View underlying SQL

### Models
- `get_all_models` / `get_mart_models` - Model discovery
- `get_model_details` - Model information
- `get_model_parents` / `get_model_children` - Lineage
- `get_model_health` - Execution status

### Sources
- `get_all_sources` - Source discovery
- `get_source_details` - Configuration and freshness

### Jobs
- `list_jobs` - Available jobs
- `get_job_details` - Job configuration
- `trigger_job_run` - Execute pipelines
- `get_job_run_details` / `get_job_run_error` - Monitoring

### Advanced
- `get_exposures` - Downstream applications
- `get_semantic_model_details` - MetricFlow models
- `get_test_details` - Data quality tests

## Examples

See [examples.md](examples.md) for detailed usage patterns:
- Business metrics discovery
- Revenue analysis with dimensions
- Data quality checks
- Pipeline management
- Model exploration

## Error Handling

| Problem | Solution |
|---------|----------|
| Tools not found | Use `tool_search_tool_regex` to verify availability |
| Metric unavailable | Check `list_metrics` for alternatives |
| Stale data | Use `get_model_health` and source freshness |
| Job failure | Use `get_job_run_error` for diagnostics |

If dbt tools unavailable, inform user and fall back to alternative methods.
