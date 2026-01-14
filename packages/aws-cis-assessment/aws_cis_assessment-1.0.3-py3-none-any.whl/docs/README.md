# AWS CIS Controls Compliance Assessment Tool Documentation

Welcome to the comprehensive documentation for the AWS CIS Controls Compliance Assessment Tool. This tool evaluates AWS account security posture against CIS Controls Implementation Groups (IG1, IG2, IG3) using AWS Config rule specifications without requiring AWS Config to be enabled.

## Documentation Structure

### User Documentation
- **[Installation Guide](installation.md)** - Complete installation and setup instructions
- **[User Guide](user-guide.md)** - Comprehensive usage guide with examples
- **[Configuration Guide](configuration.md)** - Configuration options and customization
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

### Developer Documentation
- **[Developer Guide](developer-guide.md)** - Extending and customizing assessments
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Architecture Guide](architecture.md)** - System architecture and design

### Reference Documentation
- **[Config Rule Mappings](config-rule-mappings.md)** - Complete mapping of CIS Controls to AWS Config rules
- **[Assessment Logic](assessment-logic.md)** - Detailed assessment logic documentation
- **[CLI Reference](cli-reference.md)** - Complete command-line interface reference

## Quick Start

1. **Install the tool**: `pip install aws-cis-assessment`
2. **Configure AWS credentials**: `aws configure` or set environment variables
3. **Run basic assessment**: `aws-cis-assess assess`
4. **View results**: Open the generated HTML report

## Key Features

- **Comprehensive Coverage**: 100+ AWS Config rules mapped to CIS Controls
- **Implementation Groups**: IG1 (Essential), IG2 (Enhanced), IG3 (Advanced)
- **Multiple Output Formats**: JSON, HTML, and CSV reports
- **No AWS Config Required**: Direct AWS API calls based on Config rule specifications
- **Enterprise Ready**: Handles large-scale assessments with proper error handling

## Implementation Groups Overview

### IG1 - Essential Cyber Hygiene (56 Config Rules)
Foundational safeguards for all enterprises:
- Asset Inventory and Management
- Basic Access Controls
- Secure Configuration Baselines
- Password Management

### IG2 - Enhanced Security (+30 Config Rules)
Additional controls for regulated environments:
- Encryption in Transit and at Rest
- Advanced Access Controls
- Vulnerability Management
- Network Security

### IG3 - Advanced Security (+20 Config Rules)
Sophisticated controls for high-risk environments:
- Sensitive Data Logging
- Network Segmentation
- Application Security
- Advanced Monitoring

## Support and Contributing

- **Issues**: Report bugs and request features on GitHub
- **Contributing**: See the developer guide for contribution guidelines
- **Community**: Join our community discussions

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.