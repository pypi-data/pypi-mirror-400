# CFabric Benchmarks

Benchmark suite for comparing Context-Fabric (CF) vs Text-Fabric (TF) performance across memory usage, query latency, and multi-corpus scaling.

## Prerequisites

### 1. Activate the Virtual Environment

From the repository root:

```bash
source .venv/bin/activate
```

### 2. Install the Package

From the `libs/benchmarks` directory:

```bash
pip install -e .
```

### 3. Download Test Corpora

The benchmarks require Text-Fabric corpora. Download them using the built-in script:

```bash
python -m cfabric_benchmarks.corpora.download
```

This downloads 10 biblical studies corpora to `.corpora/` (approximately 3GB total):
- **cuc** - Copenhagen Ugaritic Corpus (smallest, ~1.6 MB)
- **tischendorf** - Tischendorf 8th Edition Greek NT (~34 MB)
- **syrnt** - Syriac New Testament (~52 MB)
- **peshitta** - Syriac Old Testament (~55 MB)
- **quran** - Quranic Arabic Corpus (~73 MB)
- **sp** - Samaritan Pentateuch (~147 MB)
- **lxx** - Septuagint (~268 MB)
- **n1904** - Nestle 1904 Greek NT (~319 MB)
- **dss** - Dead Sea Scrolls (~936 MB)
- **bhsa** - Biblia Hebraica Stuttgartensia Amstelodamensis 2021 (~1.1 GB)

### 4. Validate Corpora Loading

Before running benchmarks, validate that corpora load correctly in both Text-Fabric and Context-Fabric:

```bash
python -m cfabric_benchmarks.corpora.validate
```

Or validate a single corpus:

```bash
python -m cfabric_benchmarks.corpora.validate --corpus sp
```

---

## Benchmark Types

### 1. Memory Benchmark

Measures memory consumption for Text-Fabric (TF) and Context-Fabric (CF) across three modes:

- **Single-process**: Memory for loading a corpus in one process
- **Spawn mode**: Memory when spawning N worker processes (each loads independently)
- **Fork mode**: Memory when forking N workers (shares parent memory via CoW)

#### Run Memory Benchmark

```bash
# All corpora
cfabric-bench memory --corpora-dir .corpora

# Specific corpora
cfabric-bench memory -c bhsa -c sp --corpora-dir .corpora

# Custom parameters
cfabric-bench memory \
    --corpora-dir .corpora \
    --runs 5 \
    --warmup 1 \
    --workers 4 \
    --output-dir ./benchmark_results
```

#### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--corpus, -c` | all | Corpus name(s) to benchmark (repeatable) |
| `--runs` | 5 | Number of benchmark runs for averaging |
| `--warmup` | 1 | Warmup runs (excluded from statistics) |
| `--workers` | 4 | Number of workers for spawn/fork tests |
| `--corpora-dir` | `./corpora` | Directory containing corpora |
| `--output-dir` | `./benchmark_results` | Output directory |

#### Output

- `memory_raw_{corpus}.csv` - Raw measurements per run
- `memory_summary.csv` - Statistical summary
- `cross_corpus_summary.csv` - Comparison across corpora
- `fig_memory_{corpus}.pdf/png` - Visualization charts

---

### 2. Latency Benchmark

Measures search query execution time for TF vs CF using curated query patterns.

**Note:** Currently only supports the BHSA corpus (has curated query patterns).

#### Run Latency Benchmark

```bash
cfabric-bench latency --corpus bhsa --corpora-dir .corpora

# Custom parameters
cfabric-bench latency \
    --corpus bhsa \
    --corpora-dir .corpora \
    --queries 50 \
    --iterations 10 \
    --runs 5 \
    --output-dir ./benchmark_results
```

#### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--corpus, -c` | required | Corpus to benchmark (must be `bhsa`) |
| `--queries` | 50 | Number of search patterns to test |
| `--iterations` | 10 | Iterations per pattern |
| `--runs` | 5 | Number of benchmark runs |
| `--validation-corpus` | smallest | Corpus for pattern validation |
| `--corpora-dir` | `./corpora` | Directory containing corpora |
| `--output-dir` | `./benchmark_results` | Output directory |

#### Output

- `queries.json` - The search patterns used
- `latency_raw.csv` - Raw timing measurements
- `latency_statistics.csv` - Statistical summary per query
- `fig_latency_distribution.pdf/png` - Latency distribution chart
- `fig_latency_percentiles.pdf/png` - Percentile comparison chart

---

### 3. Progressive Loading Benchmark

Measures how memory scales as multiple corpora are loaded sequentially. Tests memory efficiency and scaling characteristics.

#### Run Progressive Benchmark

```bash
cfabric-bench progressive --corpora-dir .corpora

# Custom parameters
cfabric-bench progressive \
    --corpora-dir .corpora \
    --max-corpora 10 \
    --runs 5 \
    --output-dir ./benchmark_results
```

#### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-corpora` | 10 | Maximum corpora to load progressively |
| `--runs` | 5 | Number of benchmark runs |
| `--corpora-dir` | `./corpora` | Directory containing corpora |
| `--output-dir` | `./benchmark_results` | Output directory |

Corpora are loaded smallest to largest based on a predefined size order.

#### Output

- `progressive_steps.csv` - Memory at each loading step
- `scaling_analysis.json` - Linear regression analysis of memory scaling
- `fig_scaling_progressive.pdf/png` - Scaling visualization

---

## Full Benchmark Suite

Run all three benchmark types in one command:

```bash
cfabric-bench full --corpora-dir .corpora

# Custom parameters
cfabric-bench full \
    --corpora-dir .corpora \
    --memory-runs 10 \
    --latency-runs 5 \
    --progressive-runs 5 \
    --warmup 2 \
    --workers 4 \
    --queries 100 \
    --iterations 10 \
    --max-corpora 10 \
    --output-dir ./benchmark_results
```

#### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--memory-runs` | 5 | Number of runs for memory benchmark |
| `--latency-runs` | 5 | Number of runs for latency benchmark |
| `--progressive-runs` | 5 | Number of runs for progressive benchmark |
| `--warmup` | 1 | Warmup runs (excluded from statistics) |
| `--workers` | 4 | Workers for memory spawn/fork tests |
| `--queries` | 50 | Number of search patterns for latency |
| `--iterations` | 10 | Iterations per query for latency |
| `--max-corpora` | 10 | Maximum corpora for progressive loading |
| `--corpora-dir` | `.corpora` | Directory containing corpora |
| `--output-dir` | `./benchmark_results` | Output directory |
| `--no-pdf` | - | Skip PDF chart generation |

### Full Suite Output Structure

```
benchmark_results/YYYY-MM-DD_HHMMSS/
├── config.json              # Benchmark configuration
├── environment.json         # System/software metadata
├── report.pdf               # Combined PDF report
├── memory/
│   ├── raw_{corpus}.csv
│   ├── summary.csv
│   └── cross_corpus_summary.csv
├── latency/
│   ├── queries.json
│   ├── raw_measurements.csv
│   └── statistics.csv
└── progressive/
    ├── raw_steps.csv
    └── scaling_analysis.json
```

---

## Utility Commands

### Check Environment

Display system and software information:

```bash
cfabric-bench environment
```

### Validate Query Patterns

Validate curated BHSA patterns before running latency benchmarks:

```bash
cfabric-bench validate-patterns --corpora-dir .corpora
```

### Regenerate Visualizations

Regenerate charts from existing benchmark results without re-running benchmarks. Useful after modifying chart code or for creating different output formats.

```bash
# Regenerate all supported charts (progressive, latency, multicorpus)
cfabric-bench visualize ./benchmark_results/YYYY-MM-DD_HHMMSS

# Regenerate specific chart types only
cfabric-bench visualize ./benchmark_results/YYYY-MM-DD_HHMMSS --charts progressive
cfabric-bench visualize ./benchmark_results/YYYY-MM-DD_HHMMSS --charts latency,multicorpus

# Control output format
cfabric-bench visualize ./benchmark_results/YYYY-MM-DD_HHMMSS --format pdf
cfabric-bench visualize ./benchmark_results/YYYY-MM-DD_HHMMSS --format png
cfabric-bench visualize ./benchmark_results/YYYY-MM-DD_HHMMSS --format both
```

#### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--charts, -c` | `progressive,latency,multicorpus` | Chart types to generate (comma-separated) |
| `--format, -f` | `both` | Output format: `pdf`, `png`, or `both` |

#### Supported Chart Types

| Type | Charts Generated | Data Source |
|------|------------------|-------------|
| `progressive` | `fig_scaling_progressive.pdf/png` | `progressive/raw_steps.csv` |
| `latency` | `fig_latency_distribution.pdf/png`, `fig_latency_percentiles.pdf/png` | `latency/queries.json`, `latency/raw_measurements.csv` |
| `multicorpus` | `fig_memory_multicorpus.pdf/png` | `memory/summary.csv` |

**Note:** Per-corpus memory charts (`fig_memory_{corpus}.pdf`) cannot be regenerated as they require corpus metadata not stored in CSV files. These are only generated during the initial benchmark run.

---

## Quick Start Example

```bash
# Setup (from repository root)
source .venv/bin/activate
cd libs/benchmarks
pip install -e .

# Download corpora
python -m cfabric_benchmarks.corpora.download

# Validate it works
python -m cfabric_benchmarks.corpora.validate --corpus sp

# Run memory benchmark on small corpus
cfabric-bench memory -c sp --corpora-dir .corpora --runs 3

# Run full suite (takes longer)
cfabric-bench full --corpora-dir .corpora --memory-runs 3 --latency-runs 3 --progressive-runs 3 --max-corpora 5
```
