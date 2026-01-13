# **PipeX v2.0** 

**A powerful, enterprise-grade CLI-based ETL pipeline automation tool for modern data engineering workflows.**

PipeX simplifies complex data pipeline tasks with multi-cloud support, intelligent error handling, and industry-specific transformations. Built for scalability, reliability, and ease of use.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-Cloud](https://img.shields.io/badge/Multi--Cloud-AWS%20%7C%20GCP%20%7C%20Azure%20%7C%20DO-green.svg)](https://github.com/yourusername/pipex)

---

## **Key Features**

### **Comprehensive ETL Operations**

- **Extract** from APIs, databases (SQL/NoSQL), and files (CSV, JSON, Excel, Parquet, XML)
- **Transform** with custom Python scripts, default templates, and industry-specific functions
- **Load** to multi-cloud storage, databases, and local files with automatic organization

### **Multi-Cloud Storage Support**

- **AWS S3** - Full S3 API compatibility with IAM roles
- **Google Cloud Storage** - Service account and project-based authentication
- **Azure Blob Storage** - Connection string and account key authentication
- **DigitalOcean Spaces** - S3-compatible API with regional deployment

### **Intelligent Error Handling**

- **User-friendly error messages** with clear problem descriptions
- **Actionable solutions** for every error scenario
- **Context-aware guidance** based on error category and environment
- **Technical details** for debugging without overwhelming users

### **Advanced Transformations**

- **Multiple script execution** in sequence with fail-safe options
- **Default transformation library** with data cleaning, feature engineering, and validation
- **Industry-specific templates** for Finance, Retail, Healthcare, and Manufacturing
- **Configuration-based transformations** for common operations

### **Multi-Format File Support**

- **Excel files** with sheet selection, range options, and formula support
- **Parquet format** for high-performance columnar storage and analytics
- **XML parsing** with XPath support for structured data extraction
- **Enhanced CSV/JSON** with encoding, delimiter, and orientation options

---

## **Quick Start**

### **Installation**

#### **Basic Installation**

```bash
pip install pipex
```

#### **With Cloud Provider Support**

```bash
pip install pipex[aws]        # AWS S3 support
pip install pipex[gcp]        # Google Cloud Storage
pip install pipex[azure]      # Azure Blob Storage
pip install pipex[all]        # All cloud providers + file formats
```

#### **Development Installation**

```bash
git clone https://github.com/yourusername/pipex.git
cd pipex
pip install -e .[all]
```

### **Basic Usage**

1. **Create configuration file** (`config.yaml`):

```yaml
extract:
  source: "api"
  connection_details:
    headers:
      Authorization: "Bearer ${API_TOKEN}"
  query_or_endpoint: "${API_ENDPOINT}"

transform:
  scripts:
    - "app/default_transforms.py"
  config:
    use_default_transforms: true
    default_config:
      clean_data: true
      feature_engineering: true

load:
  target: "Cloud Storage"
  config:
    provider: "aws"
    bucket_name: "${AWS_BUCKET_NAME}"
    file_name: "processed_data.csv"
```

2. **Set environment variables** (`.env` file):

```bash
API_TOKEN=your-api-token
API_ENDPOINT=https://api.example.com/data
AWS_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

3. **Run the pipeline**:

```bash
pipex run --config config.yaml
```

---

## **Commands**

### **Pipeline Operations**

```bash
# Run complete ETL pipeline
pipex run --config config.yaml

# Validate configuration before execution
pipex validate config.yaml

# Dry run (validate without executing)
pipex run --config config.yaml --dry-run

# Verbose logging for debugging
pipex run --config config.yaml --verbose
```

### **Individual Stage Operations**

```bash
# Extract data only
pipex extract api config.yaml --output extracted_data.csv

# Transform data with custom scripts
pipex transform scripts/clean.py config.yaml data.csv --output clean_data.csv

# Load data to target
pipex load "Cloud Storage" config.yaml processed_data.csv
```

### **System Information**

```bash
# Display system status and configuration
pipex info

# Get help for any command
pipex --help
pipex run --help
```

---

## **Configuration Examples**

### **Multi-Cloud Storage**

#### **AWS S3**

```yaml
load:
  target: "Cloud Storage"
  config:
    provider: "aws"
    bucket_name: "${AWS_BUCKET_NAME}"
    file_name: "data.parquet"
    format: "parquet"
    aws_access_key_id: "${AWS_ACCESS_KEY_ID}"
    aws_secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    region_name: "${AWS_REGION}"
```

#### **Google Cloud Storage**

```yaml
load:
  target: "Cloud Storage"
  config:
    provider: "gcp"
    bucket_name: "${GCP_BUCKET_NAME}"
    file_name: "data.json"
    format: "json"
    project_id: "${GOOGLE_CLOUD_PROJECT}"
    credentials_path: "${GOOGLE_APPLICATION_CREDENTIALS}"
```

#### **Azure Blob Storage**

```yaml
load:
  target: "Cloud Storage"
  config:
    provider: "azure"
    bucket_name: "${AZURE_CONTAINER_NAME}"
    file_name: "data.csv"
    format: "csv"
    connection_string: "${AZURE_STORAGE_CONNECTION_STRING}"
```

### **Advanced File Processing**

#### **Excel to Parquet Pipeline**

```yaml
extract:
  source: "file"
  connection_details:
    file_type: "excel"
    sheet_name: "Sheet1"
    skiprows: 2
    nrows: 10000
    engine: "openpyxl"
  query_or_endpoint: "data/input.xlsx"

load:
  target: "Local File"
  config:
    file_type: "parquet"
    file_path: "output/processed_data.parquet"
    compression: "snappy"
```

#### **API to Multi-Format**

```yaml
extract:
  source: "api"
  connection_details:
    headers:
      X-API-Key: "${API_KEY}"
    timeout: 60
  query_or_endpoint: "${API_ENDPOINT}"

load:
  target: "Local File"
  config:
    file_type: "excel"
    file_path: "output/api_data.xlsx"
    sheet_name: "APIData"
    add_timestamp: true
```

### **Advanced Transformations**

#### **Multiple Scripts with Industry Templates**

```yaml
transform:
  scripts:
    - "app/default_transforms.py"
    - "transforms/industry_specific.py"
    - "transforms/custom_business_rules.py"
  config:
    use_default_transforms: true
    fail_on_script_error: false
    default_config:
      clean_data: true
      feature_engineering: true
      add_metadata: true
    script_config:
      industry: "finance"
      large_transaction_threshold: 10000
```

#### **Configuration-Based Transformations**

```yaml
transform:
  config:
    drop_columns: ["temp_id", "debug_info"]
    rename_columns:
      customer_name: "client_name"
      order_date: "purchase_date"
    filter_rows: "amount > 0 & status == 'active'"
    add_columns:
      total_value: "price * quantity"
      processed_date: "pd.Timestamp.now()"
      is_high_value: "total_value > 1000"
```

---

## **Data Sources & Targets**

### **Supported Data Sources**

| Source Type   | Formats                        | Authentication                    | Features                      |
| ------------- | ------------------------------ | --------------------------------- | ----------------------------- |
| **APIs**      | JSON, XML                      | Bearer Token, API Key, Basic Auth | Retry logic, caching, timeout |
| **Databases** | SQL, NoSQL                     | Connection strings, credentials   | MySQL, PostgreSQL, MongoDB    |
| **Files**     | CSV, JSON, Excel, Parquet, XML | File system access                | Encoding, delimiters, sheets  |

### **Supported Targets**

| Target Type       | Providers                        | Formats                   | Features                       |
| ----------------- | -------------------------------- | ------------------------- | ------------------------------ |
| **Cloud Storage** | AWS S3, GCP, Azure, DigitalOcean | CSV, JSON, Parquet        | Multi-region, encryption       |
| **Databases**     | MySQL, PostgreSQL, MongoDB       | Native formats            | Batch loading, upserts         |
| **Local Files**   | File system                      | CSV, JSON, Excel, Parquet | Directory creation, timestamps |

---

## **Industry-Specific Templates**

### **Financial Services**

```python
# Automatic risk scoring, compliance checks, transaction analysis
transform:
  scripts: ["transforms/industry_specific.py"]
  config:
    script_config:
      industry: "finance"
      large_transaction_threshold: 10000
      compliance_checks: true
```

**Features:**

- Transaction risk scoring
- Money laundering detection
- Regulatory compliance flags
- Fiscal year calculations
- Business day analysis

### **Retail & E-commerce**

```python
# Customer segmentation, lifetime value, seasonal analysis
transform:
  scripts: ["transforms/industry_specific.py"]
  config:
    script_config:
      industry: "retail"
      customer_segmentation: true
```

**Features:**

- Customer lifetime value (CLV) estimation
- RFM analysis (Recency, Frequency, Monetary)
- Seasonal trend detection
- Product category analysis
- Customer tier classification

### **Healthcare**

```python
# Patient demographics, risk stratification, medical coding
transform:
  scripts: ["transforms/industry_specific.py"]
  config:
    script_config:
      industry: "healthcare"
      risk_stratification: true
```

**Features:**

- Age group classification
- Risk score calculation
- ICD-10 code processing
- Length of stay analysis
- Chronic condition flagging

### **Manufacturing**

```python
# Quality metrics, equipment efficiency, cost analysis
transform:
  scripts: ["transforms/industry_specific.py"]
  config:
    script_config:
      industry: "manufacturing"
      efficiency_threshold: 0.85
```

**Features:**

- Equipment efficiency tracking
- Quality grade classification
- Shift analysis
- Defect rate calculation
- Maintenance scheduling

---

## **Error Handling & Troubleshooting**

### **Intelligent Error Messages**

PipeX provides context-aware error messages with actionable solutions:

```
Configuration Error: Environment variable placeholders are not resolved

📋 Context:
  • config_file: config.yaml
  • missing_variables: API_TOKEN, AWS_BUCKET_NAME

  Suggested Solutions:
  1. Create a .env file in your project root
  2. Set the required environment variables (check .env.example)
  3. Ensure environment variable names match the placeholders in config
  4. Use format ${VARIABLE_NAME} for placeholders in config file

Technical Details: Unresolved placeholders: ${API_TOKEN}, ${AWS_BUCKET_NAME}
```

### **Common Issues & Solutions**

#### **Authentication Errors**

```bash
# Check credentials
pipex info

# Set AWS credentials
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Validate configuration
pipex validate config.yaml
```

#### **File Format Issues**

```bash
# Test with verbose logging
pipex run --config config.yaml --verbose

# Check file encoding
pipex extract file config.yaml --output test.csv
```

#### **Network Issues**

```bash
# Test API connectivity
curl -H "Authorization: Bearer $API_TOKEN" $API_ENDPOINT

# Check timeout settings in config
pipex run --config config.yaml --dry-run
```

---

## **Environment Variables**

### **Multi-Cloud Credentials**

```bash
# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Azure
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
# OR
AZURE_STORAGE_ACCOUNT_NAME=your-account
AZURE_STORAGE_ACCOUNT_KEY=your-key

# DigitalOcean Spaces
DO_SPACES_ACCESS_KEY_ID=your-key
DO_SPACES_SECRET_ACCESS_KEY=your-secret
DO_SPACES_REGION=nyc3
```

### **API & Database Credentials**

```bash
# API Authentication
API_TOKEN=your-bearer-token
API_KEY=your-api-key
API_ENDPOINT=https://api.example.com/data

# Database Connections
DB_HOST=localhost
DB_USER=username
DB_PASSWORD=password
DB_NAME=database_name

# MongoDB
MONGO_HOST=localhost
MONGO_USER=username
MONGO_PASSWORD=password
MONGO_DATABASE=database_name
```

---

## **Performance & Scalability**

### **Optimization Features**

- **Chunked processing** for large datasets
- **Memory-efficient** transformations with pandas
- **Parallel script execution** for complex pipelines
- **Connection pooling** for database operations
- **Streaming uploads** for cloud storage
- **Compression support** for all file formats

### **Benchmarks**

| Dataset Size | Processing Time | Memory Usage | Throughput        |
| ------------ | --------------- | ------------ | ----------------- |
| 10K records  | 2-5 seconds     | 15-25 MB     | 2K-5K records/sec |
| 100K records | 15-30 seconds   | 50-100 MB    | 3K-7K records/sec |
| 1M records   | 2-5 minutes     | 200-500 MB   | 3K-8K records/sec |

### **Scaling Recommendations**

- Use **Parquet format** for large datasets (10x faster than CSV)
- Enable **chunked processing** for files > 1GB
- Use **cloud storage** for distributed processing
- Implement **data partitioning** for very large datasets

---

## **Integration Examples**

### **CI/CD Pipeline**

```yaml
# GitHub Actions
name: Data Pipeline
on:
  schedule:
    - cron: "0 2 * * *" # Daily at 2 AM

jobs:
  etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"
      - name: Install PipeX
        run: pip install pipex[all]
      - name: Validate Configuration
        run: pipex validate config.yaml
      - name: Run ETL Pipeline
        run: pipex run --config config.yaml
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### **Docker Deployment**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .[all]

CMD ["pipex", "run", "--config", "config.yaml"]
```

### **Kubernetes CronJob**

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pipex-etl
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: pipex
              image: your-registry/pipex:latest
              command: ["pipex", "run", "--config", "config.yaml"]
              env:
                - name: API_TOKEN
                  valueFrom:
                    secretKeyRef:
                      name: pipex-secrets
                      key: api-token
          restartPolicy: OnFailure
```

---

## **🧪 Testing & Development**

### **Running Tests**

```bash
# Install development dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_extract.py -v
pytest tests/test_transform.py -v
pytest tests/test_load.py -v
```

### **Code Quality**

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linting
flake8 app/ tests/
```

### **Development Setup**

```bash
# Clone repository
git clone https://github.com/yourusername/pipex.git
cd pipex

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[all,dev]

# Run tests
pytest
```

---

## **📚 Documentation & Examples**

### **Configuration Templates**

- [`examples/multi_cloud_config.yaml`](examples/multi_cloud_config.yaml) - Multi-cloud storage examples
- [`examples/transforms/`](examples/transforms/) - Custom transformation scripts
- [`.env.example`](.env.example) - Environment variable template

### **Transformation Scripts**

- [`app/default_transforms.py`](app/default_transforms.py) - Default transformation library
- [`examples/transforms/industry_specific.py`](examples/transforms/industry_specific.py) - Industry templates

### **Additional Resources**

- [**Usage Examples**](USAGE_EXAMPLES.md) - Comprehensive usage guide
- [**New Features**](NEW_FEATURES.md) - v2.0 feature overview
- [**API Documentation**](docs/api.md) - Detailed API reference
- [**Troubleshooting Guide**](docs/troubleshooting.md) - Common issues and solutions

---

## **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### **Development Process**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### **Contribution Areas**

-  **New data sources** (databases, APIs, file formats)
-  **Additional cloud providers** (IBM Cloud, Oracle Cloud)
-  **Industry-specific transformations**
-  **Testing and quality assurance**
-  **Documentation and examples**
-  **Bug fixes and performance improvements**

---

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## **Support & Community**

### **Getting Help**

-  **Email**: agniveshkumar15@gmail.com
-  **Issues**: [GitHub Issues](https://github.com/ImCYMBIOT/pipex/issues)
-  **Discussions**: [GitHub Discussions](https://github.com/ImCYMBIOT/pipex/discussions)
<!-- -  **Documentation**: [Wiki](https://github.com/ImCYMBIOT/pipex/wiki) -->

### **Community**

- 🌟 **Star the project** if you find it useful
- 🐦 **Follow updates** on Twitter [@PipeXETL](https://twitter.com/PipeXETL)
- 📢 **Share your use cases** in GitHub Discussions
- 🤝 **Contribute** to make PipeX even better

---

## **Acknowledgments**

PipeX is built with and inspired by amazing open-source projects:

- **[Typer](https://typer.tiangolo.com/)** - Modern CLI framework
- **[Pandas](https://pandas.pydata.org/)** - Powerful data manipulation library
- **[Boto3](https://boto3.amazonaws.com/)** - AWS SDK for Python
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Database toolkit
- **[Requests](https://requests.readthedocs.io/)** - HTTP library

---

<div align="center">

**Made with ❤️ for the data engineering community**

[⭐ Star on GitHub](https://github.com/yourusername/pipex) • [📚 Documentation](https://github.com/yourusername/pipex/wiki) • [🐛 Report Bug](https://github.com/yourusername/pipex/issues) • [💡 Request Feature](https://github.com/yourusername/pipex/issues)

</div>
