# User Guide

This comprehensive guide covers how to use the AWS CIS Controls Compliance Assessment Tool effectively.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Assessment Options](#assessment-options)
4. [Output Formats](#output-formats)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Common Workflows](#common-workflows)

## Quick Start

### Your First Assessment

```bash
# Run a basic assessment with default settings
aws-cis-assess assess

# This will:
# - Assess all Implementation Groups (IG1, IG2, IG3)
# - Use all enabled AWS regions
# - Generate a JSON report
# - Use default AWS credentials
```

### Quick IG1 Assessment

```bash
# Focus on essential controls only
aws-cis-assess assess --implementation-groups IG1 --regions us-east-1
```

### Generate HTML Report

```bash
# Create an interactive web report
aws-cis-assess assess --output-format html --output-file compliance-report.html
```

## Basic Usage

### Command Structure

```bash
aws-cis-assess [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

- `--verbose, -v`: Enable verbose output
- `--debug`: Enable debug logging
- `--version`: Show version information
- `--help`: Show help information

### Main Commands

#### assess
Run CIS Controls compliance assessment

```bash
aws-cis-assess assess [OPTIONS]
```

#### list-controls
List available CIS Controls and their Config rules

```bash
aws-cis-assess list-controls [OPTIONS]
```

#### list-regions
List available AWS regions

```bash
aws-cis-assess list-regions [OPTIONS]
```

#### show-stats
Show assessment statistics and scope

```bash
aws-cis-assess show-stats [OPTIONS]
```

#### validate-credentials
Test AWS credentials and permissions

```bash
aws-cis-assess validate-credentials [OPTIONS]
```

#### validate-config
Validate CIS Controls configuration files

```bash
aws-cis-assess validate-config [OPTIONS]
```

## Assessment Options

### Implementation Groups

Choose which CIS Controls Implementation Groups to assess:

```bash
# Assess only IG1 (Essential Cyber Hygiene)
aws-cis-assess assess --implementation-groups IG1

# Assess IG1 and IG2
aws-cis-assess assess --implementation-groups IG1,IG2

# Assess all groups (default)
aws-cis-assess assess --implementation-groups IG1,IG2,IG3
```

### Specific Controls

Target specific CIS Controls:

```bash
# Assess specific controls
aws-cis-assess assess --controls 1.1,3.3,4.1

# Exclude specific controls
aws-cis-assess assess --exclude-controls 7.1,12.8
```

### Regional Scope

Control which AWS regions to assess:

```bash
# Specific regions
aws-cis-assess assess --regions us-east-1,us-west-2,eu-west-1

# Exclude regions
aws-cis-assess assess --exclude-regions us-gov-east-1,us-gov-west-1

# Single region
aws-cis-assess assess --regions us-east-1
```

### AWS Credentials

Specify AWS credentials and profiles:

```bash
# Use specific AWS profile
aws-cis-assess assess --aws-profile production

# Use access keys directly
aws-cis-assess assess --aws-access-key-id AKIA... --aws-secret-access-key ...

# Use temporary credentials
aws-cis-assess assess --aws-access-key-id AKIA... --aws-secret-access-key ... --aws-session-token ...
```

## Output Formats

### JSON Format (Default)

Machine-readable format for automation:

```bash
aws-cis-assess assess --output-format json --output-file results.json
```

JSON structure:
```json
{
  "assessment_metadata": {
    "account_id": "123456789012",
    "timestamp": "2024-01-15T10:30:00Z",
    "regions_assessed": ["us-east-1", "us-west-2"],
    "assessment_duration": "PT15M30S"
  },
  "compliance_summary": {
    "overall_compliance_percentage": 78.5,
    "ig1_compliance_percentage": 85.2,
    "ig2_compliance_percentage": 72.1,
    "ig3_compliance_percentage": 65.8
  },
  "detailed_results": {
    "IG1": {
      "controls": {
        "1.1": {
          "compliance_percentage": 90.0,
          "findings": [...]
        }
      }
    }
  }
}
```

### HTML Format

Interactive web-based report:

```bash
aws-cis-assess assess --output-format html --output-file report.html
```

Features:
- Executive dashboard with charts
- Drill-down capabilities
- Responsive design
- Remediation guidance
- Export capabilities

### CSV Format

Spreadsheet-compatible format:

```bash
aws-cis-assess assess --output-format csv --output-file results.csv
```

Includes:
- Summary CSV with overall scores
- Detailed findings CSV
- Remediation guidance CSV

### Multiple Formats

Generate multiple formats simultaneously:

```bash
aws-cis-assess assess --output-format json,html,csv --output-dir ./reports/
```

## Advanced Features

### Performance Tuning

Control assessment performance:

```bash
# Limit parallel workers
aws-cis-assess assess --max-workers 2

# Set timeout
aws-cis-assess assess --timeout 1800

# Quiet mode for automation
aws-cis-assess assess --quiet
```

### Error Handling

Configure error handling behavior:

```bash
# Enable error recovery
aws-cis-assess assess --enable-error-recovery

# Disable audit trail
aws-cis-assess assess --disable-audit-trail
```

### Logging

Control logging output:

```bash
# Set log level
aws-cis-assess assess --log-level DEBUG

# Log to file
aws-cis-assess assess --log-file assessment.log

# Verbose console output
aws-cis-assess assess --verbose
```

### Dry Run

Validate configuration without running assessment:

```bash
aws-cis-assess assess --dry-run
```

### Custom Configuration

Use custom CIS Controls configuration:

```bash
aws-cis-assess assess --config-path ./custom-config/
```

## Best Practices

### 1. Start Small

Begin with IG1 controls in a single region:

```bash
aws-cis-assess assess --implementation-groups IG1 --regions us-east-1
```

### 2. Use Dry Run

Always validate before running full assessments:

```bash
aws-cis-assess assess --dry-run
```

### 3. Preview Scope

Check what will be assessed:

```bash
aws-cis-assess show-stats --implementation-groups IG1,IG2
```

### 4. Focus on Critical Controls

Start with the most important controls:

```bash
aws-cis-assess assess --controls 1.1,3.3,5.2,6.1
```

### 5. Generate Multiple Formats

Create both viewing and automation formats:

```bash
aws-cis-assess assess --output-format html,json --output-dir ./reports/
```

### 6. Use Appropriate Regions

Focus on your primary regions:

```bash
aws-cis-assess assess --regions us-east-1,us-west-2,eu-west-1
```

### 7. Control Resource Usage

For large assessments, limit workers:

```bash
aws-cis-assess assess --max-workers 2 --timeout 3600
```

### 8. Enable Detailed Logging

For troubleshooting:

```bash
aws-cis-assess assess --log-level DEBUG --log-file debug.log
```

## Common Workflows

### Initial Security Assessment

```bash
# 1. Validate credentials
aws-cis-assess validate-credentials

# 2. Check available controls
aws-cis-assess list-controls

# 3. Preview assessment scope
aws-cis-assess show-stats

# 4. Run IG1 assessment
aws-cis-assess assess --implementation-groups IG1 --output-format html

# 5. Review results and plan improvements
```

### Regular Compliance Monitoring

```bash
# Monthly comprehensive assessment
aws-cis-assess assess \
  --output-format json,html \
  --output-dir ./monthly-reports/ \
  --log-file monthly-assessment.log

# Weekly IG1 check
aws-cis-assess assess \
  --implementation-groups IG1 \
  --quiet \
  --output-format json \
  --output-file weekly-ig1.json
```

### Focused Security Review

```bash
# Focus on specific security areas
aws-cis-assess assess \
  --controls 3.3,5.2,6.1,8.1 \
  --regions us-east-1,us-west-2 \
  --output-format html \
  --output-file security-review.html
```

### Multi-Account Assessment

```bash
# Account 1
aws-cis-assess assess \
  --aws-profile account1-prod \
  --output-file account1-results.json

# Account 2
aws-cis-assess assess \
  --aws-profile account2-prod \
  --output-file account2-results.json

# Account 3
aws-cis-assess assess \
  --aws-profile account3-prod \
  --output-file account3-results.json
```

### CI/CD Integration

```bash
#!/bin/bash
# CI/CD pipeline script

# Validate credentials
if ! aws-cis-assess validate-credentials --aws-profile ci-role; then
    echo "Credential validation failed"
    exit 1
fi

# Run assessment
aws-cis-assess assess \
  --aws-profile ci-role \
  --implementation-groups IG1 \
  --quiet \
  --output-format json \
  --output-file ci-results.json

# Check compliance threshold
COMPLIANCE=$(jq -r '.compliance_summary.ig1_compliance_percentage' ci-results.json)
THRESHOLD=80

if (( $(echo "$COMPLIANCE < $THRESHOLD" | bc -l) )); then
    echo "Compliance below threshold: $COMPLIANCE% < $THRESHOLD%"
    exit 1
fi

echo "Compliance check passed: $COMPLIANCE%"
```

### Troubleshooting Workflow

```bash
# 1. Enable debug logging
aws-cis-assess assess \
  --log-level DEBUG \
  --log-file debug.log \
  --verbose

# 2. Check specific regions
aws-cis-assess list-regions --aws-profile problematic-profile

# 3. Test credentials
aws-cis-assess validate-credentials --aws-profile problematic-profile

# 4. Validate configuration
aws-cis-assess validate-config

# 5. Run limited scope
aws-cis-assess assess \
  --controls 1.1 \
  --regions us-east-1 \
  --verbose
```

## Understanding Results

### Compliance Scores

- **Overall Compliance**: Weighted average across all Implementation Groups
- **IG1 Compliance**: Essential cyber hygiene controls
- **IG2 Compliance**: Enhanced security controls (includes IG1)
- **IG3 Compliance**: Advanced security controls (includes IG1+IG2)

### Finding Status

- **COMPLIANT**: Resource meets the control requirements
- **NON_COMPLIANT**: Resource violates the control requirements
- **NOT_APPLICABLE**: Control doesn't apply to this resource
- **INSUFFICIENT_PERMISSIONS**: Cannot assess due to permission issues
- **ERROR**: Assessment failed due to technical issues

### Remediation Guidance

Each non-compliant finding includes:
- Specific remediation steps
- AWS documentation links
- Priority level (HIGH, MEDIUM, LOW)
- Estimated effort

## Next Steps

- **Configuration Guide**: Learn about customizing assessments
- **Troubleshooting Guide**: Resolve common issues
- **CLI Reference**: Complete command reference
- **Developer Guide**: Extend and customize the tool