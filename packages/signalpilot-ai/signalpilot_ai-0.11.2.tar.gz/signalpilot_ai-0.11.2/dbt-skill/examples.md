# dbt Skill Examples

## Business Metrics Discovery

**User:** "What business metrics do we have?"

```
1. tool_search_tool_regex pattern:"list_metrics"
2. list_metrics()
3. get_dimensions(metrics=["key_metric"]) for each important metric
4. Present organized view of business capabilities
```

## Revenue Analysis

**User:** "Show me revenue trends by product category this year"

```
1. list_metrics(search="revenue")
2. get_dimensions(metrics=["revenue"])
3. query_metrics(
     metrics=["revenue"],
     group_by=[
       {"name": "product_category", "type": "dimension"},
       {"name": "metric_time", "grain": "MONTH", "type": "time_dimension"}
     ],
     where="{{ TimeDimension('metric_time', 'MONTH') }} >= '2024-01-01'",
     order_by=[{"name": "metric_time", "descending": false}]
   )
```

## Data Quality Check

**User:** "Is our customer data reliable?"

```
1. get_all_models()  # Find customer-related models
2. get_model_health(uniqueId="model.project.customers")
3. get_model_parents(uniqueId="...")  # Check upstream health
4. get_all_sources()  # Check freshness
5. Report reliability assessment
```

## Pipeline Management

**User:** "Run our daily data pipeline"

```
1. list_jobs()
2. get_job_details(job_id=123)
3. trigger_job_run(job_id=123, cause="Manual trigger via AI assistant")
4. get_job_run_details(run_id=...)
5. get_job_run_error(run_id=...)  # If failure
```

## Model Exploration

**User:** "Tell me about our order processing models"

```
1. get_all_models()  # Search for order-related
2. get_model_details(uniqueId="model.project.orders")
3. get_model_parents(uniqueId="...")  # Upstream
4. get_model_children(uniqueId="...")  # Downstream
5. get_exposures()  # Applications using this data
```

## Anti-Patterns

### Wrong: Direct DB First
```
database-read_databases(table_name="orders")
```

### Right: dbt-First
```
list_metrics(search="order")
query_metrics(metrics=["total_orders"])
```

### Wrong: Skip Health Check
```
query_metrics(metrics=["revenue"])  # Unknown freshness
```

### Right: Health-Aware
```
get_model_health(uniqueId="model.project.revenue_model")
query_metrics(metrics=["revenue"])  # After confirming health
```

### Wrong: Assume Tools Exist
```
query_metrics(...)  # May not be available
```

### Right: Tool Discovery
```
tool_search_tool_regex pattern:"query_metrics"
query_metrics(...)  # After confirming exists
```
