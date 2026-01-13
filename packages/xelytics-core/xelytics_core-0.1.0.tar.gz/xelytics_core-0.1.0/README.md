# Xelytics-Core

**Pure analytics engine for statistical analysis and insight generation.**

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from xelytics import analyze, AnalysisConfig
import pandas as pd

# Load your data
df = pd.read_csv("data.csv")

# Run automated analysis
result = analyze(df, mode="automated")

# Access results
print(f"Analyzed {result.metadata.row_count} rows")
print(f"Found {len(result.statistics)} statistical tests")
print(f"Generated {len(result.visualizations)} visualizations")
print(f"Produced {len(result.insights)} insights")

# Export to JSON
json_output = result.to_json()
```

## API Contract

```python
from xelytics import analyze, AnalysisConfig, AnalysisResult

result = analyze(
    data=df,
    mode="automated",  # or "semi-automated"
    config=AnalysisConfig(
        significance_level=0.05,
        enable_llm_insights=True,
        max_visualizations=10,
    )
)
```

## Output Schema

```python
AnalysisResult(
    summary=DatasetSummary(...),
    statistics=[StatisticalTestResult(...), ...],
    visualizations=[VisualizationSpec(...), ...],
    insights=[Insight(...), ...],
    metadata=RunMetadata(...),
)
```

## Design Principles

1. **Pure analytics engine** - No HTTP, no database, no auth
2. **Deterministic** - Same input = same output
3. **LLM is optional** - Rule-based insights work without LLM
4. **Type-safe** - All inputs/outputs are typed dataclasses

## License

MIT
