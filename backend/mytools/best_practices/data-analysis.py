from mytools.best_practices import BestPracticesDocument
from mytypes.categorization import WorkflowTechnique


class DataAnalysisBestPractices(BestPracticesDocument):
    technique = WorkflowTechnique.DATA_ANALYSIS
    version = "1.0.0"

    def __init__(self) -> None:
        self._documentation = """# Best Practices: Data Analysis Workflows

## Workflow Design

Structure workflows following the Input → Transform → Output pattern. Use clear node naming (e.g., "Fetch Sales Data", "Calculate Averages", "IF High Variance?") to document the flow.

Start with appropriate triggers:
- Manual Trigger for on-demand analysis
- Cron/Schedule Trigger for periodic analysis (daily/weekly reports)
- Webhook Trigger for event-driven analysis

Break complex workflows into modular sub-workflows using the Execute Workflow node for reusable components like "Outlier Detection" or "Data Preparation".

CRITICAL: For large datasets, use Split In Batches node to process items in chunks (e.g., 100 at a time) to prevent memory issues. Always test with realistic data volumes.

Example pattern:
- Trigger → HTTP Request (fetch data) → Spreadsheet File (parse CSV) → Set (clean fields) → Filter (remove nulls) → Code (analyze) → HTML (format report) → Email (send results)

## Data Preparation Strategy

1. **Fetch Data**: Use dedicated integration nodes or HTTP Request for APIs. Import cURL commands directly to HTTP node for complex APIs.
2. **Parse & Convert**: Convert to JSON using Spreadsheet File node for CSV/Excel. Enable "Convert types where required" on condition nodes.
3. **Clean Data**: Use Set node with "Keep Only Set" enabled to drop unused fields. Filter node for removing null values or focusing on data subsets.
4. **Merge/Enrich**: Use Merge node by key or index to combine multiple sources. Choose correct merge mode to avoid mismatched items.

## Analysis Implementation

Use Function node (not Function Item) when analysis needs all items as a whole (calculating totals, finding trends). Function Item operates per item only.

For AI-powered analysis, filter irrelevant content first to minimize tokens. Batch data into single prompts when possible.

Always pin data after external calls to test downstream logic without re-fetching. This saves API costs and speeds development.

## Output & Integration

Format results appropriately:
- HTML/Markdown nodes for reports
- Set node to prepare specific output fields (totalSales, anomalyCount)
- Database nodes to store analysis history
- Webhook Response for API-triggered workflows

Use conditional branches (IF nodes) for post-analysis actions:
- Create tasks if anomalies detected
- Send alerts for critical thresholds
- Avoid infinite loops by using proper conditions

## Recommended Nodes

### HTTP Request (n8n-nodes-base.httpRequest)

**Purpose**: Fetch datasets from URLs or APIs

**Use Cases**:
- Pull data from REST APIs for analysis
- Fetch CSV/JSON files from URLs
- Query external data sources

**Best Practices**:
- Import cURL commands for complex requests
- Use authentication credentials properly
- Handle pagination for large datasets

### Spreadsheet File (n8n-nodes-base.spreadsheetFile)

**Purpose**: Parse CSV/Excel files into JSON items for processing

**Use Cases**:
- Import CSV data from file uploads
- Process Excel spreadsheets
- Convert tabular data to JSON

**Best Practices**:
- Specify correct file format
- Handle header rows properly
- Test with various file encodings

### Set / Edit Fields (n8n-nodes-base.set)

**Purpose**: Clean data, select relevant fields, rename columns, convert data types

**Key Setting**: "Keep Only Set" - drops all fields not explicitly defined

**Use Cases**:
- Remove unused columns to reduce data size
- Rename fields to standardized names
- Convert data types (string to number)
- Add calculated fields

**Best Practices**:
- Enable "Keep Only Set" to drop unused data
- Always verify output structure
- Use expressions for calculated fields

### Filter (n8n-nodes-base.filter)

**Purpose**: Remove unwanted items based on conditions

**Use Cases**:
- Remove null values
- Filter outliers before analysis
- Focus on specific data subsets

**Best Practices**:
- Filter early to reduce processing load
- Use multiple conditions when needed
- Document filter logic clearly

### IF (n8n-nodes-base.if)

**Purpose**: Branch workflow based on analysis results

**Use Cases**:
- Route anomalies vs normal data
- Trigger alerts for threshold breaches
- Create conditional outputs

**Best Practices**:
- Enable "Convert types where required" for comparisons
- Use clear condition names
- Handle both true and false branches

### Code / Function (n8n-nodes-base.function)

**Purpose**: Custom JavaScript for calculations, statistics, anomaly detection

**Use Cases**:
- Calculate statistical measures (mean, median, std dev)
- Detect outliers and anomalies
- Perform complex transformations
- Implement custom algorithms

**Best Practices**:
- Use Function node (not Function Item) for whole-dataset operations
- Return proper data structure: `return items`
- Add comments to explain logic
- Test with edge cases

**Note**: Consider using the newer Code node (n8n-nodes-base.code) as Function node is deprecated.

### Aggregate (n8n-nodes-base.aggregate)

**Purpose**: Group items, gather values into arrays, count occurrences by category

**Use Cases**:
- Group sales by region
- Count items by category
- Calculate sums and averages per group

**Best Practices**:
- Choose appropriate aggregation function
- Use grouping keys effectively
- Simplifies statistical calculations

### Split In Batches (n8n-nodes-base.splitInBatches)

**Purpose**: Process large datasets in chunks to prevent memory overload

**Use Cases**:
- Handle datasets with 1000+ items
- Process API results in batches
- Prevent workflow timeouts

**Best Practices**:
- Set appropriate batch size (e.g., 100 items)
- Test with realistic data volumes
- Use loop logic properly

### Merge (n8n-nodes-base.merge)

**Purpose**: Combine data from multiple sources by key/index

**Modes**:
- Merge by Key
- Merge by Index
- Wait mode

**Use Cases**:
- Join customer data with transaction data
- Combine multiple API responses
- Enrich data from multiple sources

**Best Practices**:
- Choose correct merge mode
- Ensure matching keys exist
- Handle missing data gracefully

### Database Nodes

**MySQL** (n8n-nodes-base.mySql)  
**Postgres** (n8n-nodes-base.postgres)  
**MongoDB** (n8n-nodes-base.mongoDb)

**Best Practices**:
- Use parameterized queries
- Query efficiently with indexes
- Store results for historical tracking

### Google Sheets (n8n-nodes-base.googleSheets)

**Purpose**: Read/write spreadsheet data

**Best Practices**:
- Use ranges efficiently
- Handle large sheets with batching
- Respect API rate limits

### AI Agent (@n8n/n8n-nodes-langchain.agent)

**Purpose**: AI-powered text analysis and pattern detection

**Best Practices**:
- Filter irrelevant content first
- Batch prompts
- Use structured outputs
- Monitor cost and latency

### HTML (n8n-nodes-base.html)

**Purpose**: Generate formatted reports

### Email (n8n-nodes-base.emailSend)

**Purpose**: Send reports automatically

## Common Pitfalls to Avoid

### Data Type Mismatches
Always convert types before comparisons and enable type conversion on IF nodes.

### Memory Issues with Large Datasets
Use Split In Batches and test with realistic volumes.

### Not Pinning Data During Development
Pin external data to reduce cost and speed iteration.

### Incorrect Aggregation Logic
Use Function (not Function Item) or Aggregate node for dataset-level calculations.

### Missing Data Cleaning
Filter nulls, normalize formats, and document assumptions.

### Poor Error Handling
Use Continue on Fail, IF guards, and error workflows.

### Hardcoded Values
Move thresholds and configs to environment variables or data stores.

### Inefficient Query Patterns
Filter and aggregate at the source whenever possible.
"""

    def get_documentation(self) -> str:
        return self._documentation
