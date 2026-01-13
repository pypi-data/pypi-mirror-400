# testdino

[![PyPI version](https://badge.fury.io/py/testdino.svg)](https://pypi.org/project/testdino/)
[![Python](https://img.shields.io/pypi/pyversions/testdino.svg)](https://pypi.org/project/testdino/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **TestDino CLI** - Cache test metadata and upload Playwright test reports to TestDino platform

## Quick Start

> **⚠️ Important:** The `testdino upload` command requires a JSON report to be generated during test execution. Make sure to:
> 1. Install required plugins: `pip install pytest-playwright-json pytest-html`
> 2. Run your tests with `--playwright-json` flag: `pytest --playwright-json=test-results/report.json`
> 3. Optionally generate HTML reports: `pytest --html=test-results/index.html --self-contained-html`



### Cache Command
```bash
# Cache test execution metadata after Playwright runs
testdino cache --token="your-api-token"

# With custom directory (recommended when test results are in a specific folder)
testdino cache --working-dir test-results --token="your-api-token"

# With verbose logging
testdino cache --working-dir test-results --verbose --token="your-api-token"
```

### Last Failed Command
```bash
# Get last failed test cases for Playwright reruns
testdino last-failed --token="your-api-token"

# Get failed tests for specific shard
testdino last-failed --shard="2/5" --token="your-api-token"

# Run only last failed tests
pytest $(testdino last-failed --token="your-api-token")
```

### Upload Command
```bash
# Upload test reports with attachments
testdino upload ./test-results --token="your-api-token"

# Upload with environment tag
testdino upload ./test-results --environment="staging" --token="your-api-token"

# Upload all attachments
testdino upload ./test-results --token="your-api-token" --upload-full-json
```

## Features

- **Test Metadata Caching** - Store test execution metadata after Playwright runs
- **Last Failed Tests** - Retrieve and rerun only failed tests for faster CI/CD pipelines
- **Shard Support** - Get failed tests for specific test shards (e.g., shard 2 of 5)
- **Environment Tagging** - Tag uploads with environment labels (staging, production, qa)
- **Zero Configuration** - Auto-discovers Playwright reports and configuration
- **Smart Shard Detection** - Automatically detects Playwright shard information
- **CI/CD Ready** - Works seamlessly with GitHub Actions, GitLab CI, Jenkins, Azure DevOps
- **Secure Authentication** - Token-based API authentication
- **Usage Limit Handling** - Clear error messages with upgrade guidance
- **Last Failed Tests** - Retrieve and rerun only failed tests for faster CI/CD pipelines
- **Zero Configuration** - Auto-discovers Playwright reports and configuration
- **Smart Shard Detection** - Automatically detects Playwright shard information
- **CI/CD Ready** - Works seamlessly with GitHub Actions, GitLab CI, Jenkins, Azure DevOps
- **Secure Authentication** - Token-based API authentication

## Commands

### Cache Command

Store test execution metadata after Playwright runs.

```bash
# Basic usage
testdino cache --token="your-token"

# With custom working directory
testdino cache --working-dir ./test-results --token="your-token"

# With verbose logging
testdino cache --verbose --token="your-token"
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--working-dir <path>` | Directory to scan for test results | Current directory |
| `--cache-id <value>` | Custom cache ID override | Auto-detected |
| `-t, --token <value>` | TestDino API token | Required |
| `-v, --verbose` | Enable verbose logging | `false` |

### Last Failed Command

Retrieve cached test failures for intelligent reruns.

```bash
# Basic usage
testdino last-failed --token="your-token"

# Run only last failed tests
pytest $(testdino last-failed --token="your-token")

# With custom branch and commit
testdino last-failed --branch="main" --commit="abc123" --token="your-token"
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--cache-id <value>` | Custom cache ID override | Auto-detected |
| `--branch <value>` | Custom branch name override | Auto-detected |
| `--commit <value>` | Custom commit hash override | Auto-detected |
| `-t, --token <value>` | TestDino API token | Required |
| `-v, --verbose` | Enable verbose logging | `false` |

### Upload Command

Upload test reports with attachments.

> **⚠️ Important:** The `testdino upload` command requires a JSON report to function. You must:
> 1. Install required plugins: `pip install pytest-playwright-json pytest-html`
> 2. Run your tests with the `--playwright-json` flag: `pytest --playwright-json=test-results/report.json`
> 3. Optionally generate HTML reports: `pytest --html=test-results/index.html --self-contained-html`

```bash
# Basic upload
testdino upload ./test-results --token="your-token"

# Upload with attachments
testdino upload ./test-results --token="your-token" --upload-images --upload-videos

# Upload all attachments
testdino upload ./test-results --token="your-token" --upload-full-json
```

**Options:**

| Option | Description |
|--------|-------------|
| `<report-directory>` | Directory containing Playwright reports (required) |
| `-t, --token <value>` | TestDino API token (required) |
| `--upload-images` | Upload image attachments |
| `--upload-videos` | Upload video attachments |
| `--upload-html` | Upload HTML reports |
| `--upload-traces` | Upload trace files |
| `--upload-files` | Upload file attachments (.md, .pdf, .txt, .log) |
| `--upload-full-json` | Upload all attachments |
| `-v, --verbose` | Enable verbose logging |

### Environment Variables

```bash
export TESTDINO_TOKEN="your-api-token"
export TESTDINO_TARGET_ENV="staging"  # Optional: Set target environment
```

## CI/CD Integration

### GitHub Actions

**Basic Example:**

```yaml
name: Playwright Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pytest pytest-playwright pytest-playwright-json pytest-html testdino
          playwright install chromium --with-deps

      - name: Run Playwright Tests
        shell: bash
        env:
          TESTDINO_TOKEN: ${{ secrets.TESTDINO_TOKEN }}
        run: |
          mkdir -p test-results

          # Case 1: Re-run failed jobs → run only failed tests
          if [[ "${{ github.run_attempt }}" -gt 1 ]]; then
            testdino last-failed --token="$TESTDINO_TOKEN" > last-failed-flags.txt
            FAILED_TESTS="$(cat last-failed-flags.txt | tail -1)"

            if [[ -z "$FAILED_TESTS" ]]; then
              exit 0
            fi

            # IMPORTANT: Use eval to preserve quotes in the -k expression
            eval "pytest $FAILED_TESTS --playwright-json=test-results/report.json --html=test-results/index.html --self-contained-html -p no:selenium -v" || true
            exit 0
          fi

          # Case 2: Normal execution (first run)
          pytest \
            --playwright-json=test-results/report.json \
            --html=test-results/index.html \
            --self-contained-html \
            -p no:selenium \
            -v || true

      - name: Cache rerun metadata
        if: always()
        run: testdino cache --working-dir test-results --token="${{ secrets.TESTDINO_TOKEN }}" -v

      - name: Upload test reports
        if: always()
        run: testdino upload ./test-results --token="${{ secrets.TESTDINO_TOKEN }}"
```

**Advanced Example with Sharding and Intelligent Reruns:**

> **Note:** Sharding is **optional**. The basic example above works perfectly without sharding. Use the advanced example below only if you want to run tests in parallel across multiple shards for faster execution. The CLI automatically detects shard configuration from environment variables (`SHARD_INDEX`, `SHARD_TOTAL`) or Playwright config, and defaults to a single shard (1/1) if none is detected.

```yaml
name: Playwright Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shardIndex: [1, 2, 3, 4, 5]
        shardTotal: [5]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-playwright pytest-playwright-json pytest-html pytest-xdist pytest-shard
          pip install testdino
          playwright install --with-deps chromium

      - name: Run Playwright Tests
        shell: bash
        env:
          TESTDINO_TOKEN: ${{ secrets.TESTDINO_TOKEN }}
          SHARD_INDEX: ${{ matrix.shardIndex }}
          SHARD_TOTAL: ${{ matrix.shardTotal }}
        run: |
          mkdir -p test-results

          # Case 1: Re-run failed jobs → run only failed tests
          if [[ "${{ github.run_attempt }}" -gt 1 ]]; then

            testdino last-failed --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }} --token="$TESTDINO_TOKEN" > last-failed-flags.txt
            FAILED_TESTS="$(cat last-failed-flags.txt | tail -1)"

            if [[ -z "$FAILED_TESTS" ]]; then
              exit 0
            fi

            # IMPORTANT: Use eval to preserve quotes in the -k expression
            # pytest-shard uses 0-indexed shard IDs, so subtract 1 from SHARD_INDEX
            # Use shard-specific report name
            SHARD_ID=$(( $SHARD_INDEX - 1 ))
            eval "pytest $FAILED_TESTS --shard-id=$SHARD_ID --num-shards=$SHARD_TOTAL --playwright-json=test-results/report-${{ matrix.shardIndex }}.json --html=test-results/index.html --self-contained-html -p no:selenium -v" || true
            exit 0
          fi

          # Case 2: Normal execution (first run) with sharding
          # pytest-shard uses 0-indexed shard IDs, so subtract 1 from SHARD_INDEX
          SHARD_ID=$(( $SHARD_INDEX - 1 ))
          # Use shard-specific report name to prevent overwriting when artifacts are merged
          pytest \
            --shard-id=$SHARD_ID \
            --num-shards=$SHARD_TOTAL \
            --playwright-json=test-results/report-${{ matrix.shardIndex }}.json \
            --html=test-results/index.html \
            --self-contained-html \
            -p no:selenium \
            -v || true

      - name: Upload HTML report
        if: ${{ !cancelled() }}
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.shardIndex }}
          path: test-results/
          retention-days: 1

      - name: Cache testdino last failed metadata
        if: always()
        env:
          TESTDINO_TOKEN: ${{ secrets.TESTDINO_TOKEN }}
          SHARD_INDEX: ${{ matrix.shardIndex }}
          SHARD_TOTAL: ${{ matrix.shardTotal }}
        run: |
          if [ -n "$TESTDINO_TOKEN" ]; then
            testdino cache --working-dir test-results --token="$TESTDINO_TOKEN"
          fi

  upload-to-testdino:
    name: Upload Test Results to TestDino
    if: ${{ always() }}
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install testdino
          pip install pytest-playwright-json

      - name: Download all test results
        uses: actions/download-artifact@v4
        with:
          pattern: test-results-*
          merge-multiple: true
          path: combined-test-results

      - name: Merge JSON reports from all shards
        run: |
          python3 -m pytest_playwright_json.merge -d combined-test-results -o combined-test-results/report.json -v

      - name: Upload to TestDino
        env:
          TESTDINO_TOKEN: ${{ secrets.TESTDINO_TOKEN }}
        run: |
          if [ -z "$TESTDINO_TOKEN" ]; then
            echo "TESTDINO_TOKEN not set, skipping upload"
            exit 0
          fi
          if [ -d "combined-test-results" ] && [ -n "$(ls -A combined-test-results 2>/dev/null)" ]; then
            # Basic upload - uploads merged JSON report
            testdino upload ./combined-test-results --token="$TESTDINO_TOKEN"
          else
            echo "No test results found to upload"
          fi
```

### GitLab CI

```yaml
image: python:3.11

stages:
  - test

playwright-tests:
  stage: test
  script:
    - pip install pytest pytest-playwright pytest-playwright-json pytest-html testdino
    - playwright install chromium --with-deps
    - pytest --playwright-json=test-results/report.json --html=test-results/index.html --self-contained-html
    - testdino upload ./test-results --token="$TESTDINO_TOKEN"
  when: always
```

### Jenkins

```groovy
pipeline {
    agent any

    environment {
        TESTDINO_TOKEN = credentials('testdino-token')
    }

    stages {
        stage('Test') {
            steps {
                sh 'pip install pytest pytest-playwright pytest-playwright-json pytest-html testdino'
                sh 'playwright install chromium --with-deps'
                sh 'pytest --playwright-json=test-results/report.json --html=test-results/index.html --self-contained-html'
                sh 'testdino upload ./test-results --token="$TESTDINO_TOKEN"'
            }
        }
    }
}
```

## Authentication

### Getting Your Token

1. Sign up at [TestDino](https://app.testdino.com)
2. Navigate to **Settings** > **API Tokens**
3. Generate a new token
4. Store it securely in your CI/CD secrets

**Token Format:**
```
trx_{environment}_{64-character-hex-string}
```

**Security Best Practices:**
- Never commit tokens to version control
- Use environment variables or CI/CD secrets
- Rotate tokens regularly

## Examples

### Basic Workflow

```bash
# Run tests with JSON and HTML reports
pytest \
  --playwright-json=test-results/report.json \
  --html=test-results/index.html \
  --self-contained-html

# Cache metadata (specify directory where test results are located)
testdino cache --working-dir test-results --token="your-token"
```

### Intelligent Test Reruns

```bash
# Run tests with JSON and HTML reports, then cache results
pytest \
  --playwright-json=test-results/report.json \
  --html=test-results/index.html \
  --self-contained-html
testdino cache --working-dir test-results --token="your-token"

# On next run, execute only previously failed tests
pytest $(testdino last-failed --token="your-token")
```

### Complete CI/CD Workflow

```bash
# Run all tests with JSON and HTML reports
pytest \
  --playwright-json=test-results/report.json \
  --html=test-results/index.html \
  --self-contained-html

# Cache test metadata (specify directory where test results are located)
testdino cache --working-dir test-results --token="$TESTDINO_TOKEN"

# Rerun only failed tests
if [ $? -ne 0 ]; then
  FAILED=$(testdino last-failed --token="$TESTDINO_TOKEN")
  [ -n "$FAILED" ] && pytest $FAILED
fi
```

## Support

- **Documentation**: [docs.testdino.com](https://docs.testdino.com)
- **Issues**: [GitHub Issues](https://github.com/testdino-hq/testdino-py-cli/issues)
- **Email**: support@testdino.com

---

**Made with love by the [TestDino](https://testdino.com) team**
