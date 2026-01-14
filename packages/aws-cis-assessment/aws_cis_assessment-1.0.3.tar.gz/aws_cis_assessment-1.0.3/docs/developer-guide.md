# Developer Guide

This guide covers extending and customizing the AWS CIS Controls Compliance Assessment Tool for developers.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Adding New Controls](#adding-new-controls)
4. [Creating Custom Assessments](#creating-custom-assessments)
5. [Extending Reporters](#extending-reporters)
6. [Testing Framework](#testing-framework)
7. [Contributing Guidelines](#contributing-guidelines)
8. [API Reference](#api-reference)

## Architecture Overview

### Core Components

```
aws_cis_assessment/
├── core/                    # Core assessment engine
│   ├── assessment_engine.py # Main orchestration
│   ├── aws_client_factory.py # AWS service clients
│   ├── scoring_engine.py    # Compliance scoring
│   └── models.py           # Data models
├── controls/               # Control implementations
│   ├── ig1/               # IG1 control assessments
│   ├── ig2/               # IG2 control assessments
│   └── ig3/               # IG3 control assessments
├── config/                # Configuration management
│   ├── config_loader.py   # YAML config loader
│   └── rules/             # CIS control definitions
├── reporters/             # Report generators
│   ├── json_reporter.py   # JSON output
│   ├── html_reporter.py   # HTML reports
│   └── csv_reporter.py    # CSV export
└── cli/                   # Command-line interface
    ├── main.py           # CLI entry point
    └── utils.py          # CLI utilities
```

### Key Design Patterns

1. **Strategy Pattern**: Different assessment implementations for each control
2. **Factory Pattern**: AWS client creation and management
3. **Template Method**: Base assessment framework with customizable steps
4. **Observer Pattern**: Progress reporting and callbacks
5. **Builder Pattern**: Report generation with multiple formats

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- AWS CLI (for testing)
- Virtual environment tool

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/aws-cis-assessment.git
cd aws-cis-assessment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run tests to verify setup
pytest
```

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.20.0
hypothesis>=6.70.0
boto3-stubs[essential]>=1.26.0
```

### Code Style and Quality

```bash
# Format code
black aws_cis_assessment/

# Lint code
flake8 aws_cis_assessment/

# Type checking
mypy aws_cis_assessment/

# Run all quality checks
pre-commit run --all-files
```

## Adding New Controls

### Step 1: Define Control Configuration

Add the control to the appropriate YAML file in `aws_cis_assessment/config/rules/`:

```yaml
# cis_controls_ig1.yaml
controls:
  "1.5":  # New control ID
    title: "Maintain Asset Inventory Information"
    weight: 1.0
    config_rules:
      - name: "ec2-instance-detailed-monitoring-enabled"
        resource_types: ["AWS::EC2::Instance"]
        parameters:
          detailedMonitoringEnabled: true
        description: "Ensures EC2 instances have detailed monitoring enabled"
        remediation_guidance: "Enable detailed monitoring for EC2 instances to improve asset visibility"
```

### Step 2: Create Assessment Implementation

Create a new assessment class in the appropriate IG directory:

```python
# aws_cis_assessment/controls/ig1/control_1_5.py
from typing import List, Dict, Any
from aws_cis_assessment.controls.base_control import BaseConfigRuleAssessment
from aws_cis_assessment.core.models import ComplianceResult
from aws_cis_assessment.core.aws_client_factory import AWSClientFactory

class EC2DetailedMonitoringEnabledAssessment(BaseConfigRuleAssessment):
    """
    CIS Control 1.5: Maintain Asset Inventory Information
    AWS Config Rule: ec2-instance-detailed-monitoring-enabled
    """
    
    def __init__(self):
        super().__init__(
            rule_name="ec2-instance-detailed-monitoring-enabled",
            control_id="1.5",
            resource_types=["AWS::EC2::Instance"],
            parameters={"detailedMonitoringEnabled": True}
        )
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], 
                                    aws_factory: AWSClientFactory) -> ComplianceResult:
        """Evaluate compliance for individual EC2 instance."""
        instance_id = resource['InstanceId']
        region = resource.get('Region', 'us-east-1')
        
        try:
            ec2_client = aws_factory.get_client('ec2', region)
            
            # Check if detailed monitoring is enabled
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    monitoring_state = instance.get('Monitoring', {}).get('State', 'disabled')
                    
                    if monitoring_state == 'enabled':
                        return ComplianceResult(
                            resource_id=instance_id,
                            resource_type="AWS::EC2::Instance",
                            compliance_status="COMPLIANT",
                            evaluation_reason="Detailed monitoring is enabled",
                            config_rule_name=self.rule_name,
                            region=region,
                            timestamp=self._get_current_timestamp()
                        )
                    else:
                        return ComplianceResult(
                            resource_id=instance_id,
                            resource_type="AWS::EC2::Instance",
                            compliance_status="NON_COMPLIANT",
                            evaluation_reason=f"Detailed monitoring is {monitoring_state}",
                            config_rule_name=self.rule_name,
                            region=region,
                            timestamp=self._get_current_timestamp(),
                            remediation_guidance="Enable detailed monitoring: aws ec2 monitor-instances --instance-ids " + instance_id
                        )
            
        except Exception as e:
            return self._create_error_result(instance_id, region, str(e))
        
        return self._create_not_applicable_result(instance_id, region)
    
    def _get_resources(self, aws_factory: AWSClientFactory, 
                      resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Discover EC2 instances in the region."""
        try:
            ec2_client = aws_factory.get_client('ec2', region)
            
            response = ec2_client.describe_instances(
                Filters=[
                    {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
                ]
            )
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'InstanceId': instance['InstanceId'],
                        'InstanceType': instance['InstanceType'],
                        'State': instance['State']['Name'],
                        'Region': region
                    })
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Failed to discover EC2 instances in {region}: {str(e)}")
            return []
```

### Step 3: Register the Assessment

Add the assessment to the control registry:

```python
# aws_cis_assessment/controls/ig1/__init__.py
from .control_1_5 import EC2DetailedMonitoringEnabledAssessment

# Add to the registry
CONTROL_ASSESSMENTS = {
    # ... existing assessments
    "1.5": [EC2DetailedMonitoringEnabledAssessment],
}
```

### Step 4: Add Tests

Create comprehensive tests for the new control:

```python
# tests/test_control_1_5_assessments.py
import pytest
from unittest.mock import Mock, patch
from aws_cis_assessment.controls.ig1.control_1_5 import EC2DetailedMonitoringEnabledAssessment

class TestEC2DetailedMonitoringEnabledAssessment:
    
    def setup_method(self):
        self.assessment = EC2DetailedMonitoringEnabledAssessment()
        self.mock_aws_factory = Mock()
    
    @patch('boto3.client')
    def test_compliant_instance(self, mock_boto_client):
        """Test instance with detailed monitoring enabled."""
        # Mock EC2 response
        mock_ec2 = Mock()
        mock_ec2.describe_instances.return_value = {
            'Reservations': [{
                'Instances': [{
                    'InstanceId': 'i-1234567890abcdef0',
                    'Monitoring': {'State': 'enabled'}
                }]
            }]
        }
        mock_boto_client.return_value = mock_ec2
        self.mock_aws_factory.get_client.return_value = mock_ec2
        
        # Test resource
        resource = {
            'InstanceId': 'i-1234567890abcdef0',
            'Region': 'us-east-1'
        }
        
        result = self.assessment._evaluate_resource_compliance(
            resource, self.mock_aws_factory
        )
        
        assert result.compliance_status == 'COMPLIANT'
        assert result.resource_id == 'i-1234567890abcdef0'
        assert 'enabled' in result.evaluation_reason
    
    @patch('boto3.client')
    def test_non_compliant_instance(self, mock_boto_client):
        """Test instance with detailed monitoring disabled."""
        # Mock EC2 response
        mock_ec2 = Mock()
        mock_ec2.describe_instances.return_value = {
            'Reservations': [{
                'Instances': [{
                    'InstanceId': 'i-1234567890abcdef0',
                    'Monitoring': {'State': 'disabled'}
                }]
            }]
        }
        mock_boto_client.return_value = mock_ec2
        self.mock_aws_factory.get_client.return_value = mock_ec2
        
        # Test resource
        resource = {
            'InstanceId': 'i-1234567890abcdef0',
            'Region': 'us-east-1'
        }
        
        result = self.assessment._evaluate_resource_compliance(
            resource, self.mock_aws_factory
        )
        
        assert result.compliance_status == 'NON_COMPLIANT'
        assert result.resource_id == 'i-1234567890abcdef0'
        assert 'disabled' in result.evaluation_reason
        assert result.remediation_guidance is not None
```

## Creating Custom Assessments

### Base Assessment Class

All assessments inherit from `BaseConfigRuleAssessment`:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from aws_cis_assessment.core.models import ComplianceResult
from aws_cis_assessment.core.aws_client_factory import AWSClientFactory

class BaseConfigRuleAssessment(ABC):
    """Base class for all Config rule assessments."""
    
    def __init__(self, rule_name: str, control_id: str, 
                 resource_types: List[str], parameters: Dict[str, Any]):
        self.rule_name = rule_name
        self.control_id = control_id
        self.resource_types = resource_types
        self.parameters = parameters
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], 
                                    aws_factory: AWSClientFactory) -> ComplianceResult:
        """Evaluate compliance for individual resource."""
        pass
    
    @abstractmethod
    def _get_resources(self, aws_factory: AWSClientFactory, 
                      resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Discover resources of specified type in region."""
        pass
    
    def evaluate_compliance(self, aws_factory: AWSClientFactory, 
                          region: str) -> List[ComplianceResult]:
        """Evaluate compliance for all applicable resources."""
        all_results = []
        
        for resource_type in self.resource_types:
            try:
                resources = self._get_resources(aws_factory, resource_type, region)
                
                for resource in resources:
                    result = self._evaluate_resource_compliance(resource, aws_factory)
                    all_results.append(result)
                    
            except Exception as e:
                self.logger.error(f"Failed to evaluate {resource_type} in {region}: {str(e)}")
                # Create error result
                error_result = ComplianceResult(
                    resource_id=f"ERROR-{resource_type}",
                    resource_type=resource_type,
                    compliance_status="ERROR",
                    evaluation_reason=str(e),
                    config_rule_name=self.rule_name,
                    region=region,
                    timestamp=self._get_current_timestamp()
                )
                all_results.append(error_result)
        
        return all_results
```

### Custom Assessment Example

```python
class CustomS3BucketAssessment(BaseConfigRuleAssessment):
    """Custom assessment for S3 bucket compliance."""
    
    def __init__(self):
        super().__init__(
            rule_name="custom-s3-bucket-check",
            control_id="custom.1",
            resource_types=["AWS::S3::Bucket"],
            parameters={"requireEncryption": True, "requireVersioning": True}
        )
    
    def _evaluate_resource_compliance(self, resource: Dict[str, Any], 
                                    aws_factory: AWSClientFactory) -> ComplianceResult:
        bucket_name = resource['Name']
        region = resource.get('Region', 'us-east-1')
        
        try:
            s3_client = aws_factory.get_client('s3', region)
            
            # Check encryption
            encryption_compliant = self._check_bucket_encryption(s3_client, bucket_name)
            
            # Check versioning
            versioning_compliant = self._check_bucket_versioning(s3_client, bucket_name)
            
            if encryption_compliant and versioning_compliant:
                return ComplianceResult(
                    resource_id=bucket_name,
                    resource_type="AWS::S3::Bucket",
                    compliance_status="COMPLIANT",
                    evaluation_reason="Bucket has encryption and versioning enabled",
                    config_rule_name=self.rule_name,
                    region=region,
                    timestamp=self._get_current_timestamp()
                )
            else:
                issues = []
                if not encryption_compliant:
                    issues.append("encryption disabled")
                if not versioning_compliant:
                    issues.append("versioning disabled")
                
                return ComplianceResult(
                    resource_id=bucket_name,
                    resource_type="AWS::S3::Bucket",
                    compliance_status="NON_COMPLIANT",
                    evaluation_reason=f"Bucket issues: {', '.join(issues)}",
                    config_rule_name=self.rule_name,
                    region=region,
                    timestamp=self._get_current_timestamp(),
                    remediation_guidance=self._get_remediation_guidance(issues)
                )
                
        except Exception as e:
            return self._create_error_result(bucket_name, region, str(e))
    
    def _check_bucket_encryption(self, s3_client, bucket_name: str) -> bool:
        """Check if bucket has encryption enabled."""
        try:
            response = s3_client.get_bucket_encryption(Bucket=bucket_name)
            return 'ServerSideEncryptionConfiguration' in response
        except s3_client.exceptions.NoSuchBucket:
            return False
        except Exception:
            # If we can't check, assume non-compliant
            return False
    
    def _check_bucket_versioning(self, s3_client, bucket_name: str) -> bool:
        """Check if bucket has versioning enabled."""
        try:
            response = s3_client.get_bucket_versioning(Bucket=bucket_name)
            return response.get('Status') == 'Enabled'
        except Exception:
            return False
    
    def _get_resources(self, aws_factory: AWSClientFactory, 
                      resource_type: str, region: str) -> List[Dict[str, Any]]:
        """Discover S3 buckets."""
        try:
            s3_client = aws_factory.get_client('s3', region)
            response = s3_client.list_buckets()
            
            buckets = []
            for bucket in response['Buckets']:
                # Get bucket region
                try:
                    bucket_region = s3_client.get_bucket_location(
                        Bucket=bucket['Name']
                    )['LocationConstraint'] or 'us-east-1'
                    
                    if bucket_region == region:
                        buckets.append({
                            'Name': bucket['Name'],
                            'CreationDate': bucket['CreationDate'],
                            'Region': region
                        })
                except Exception:
                    # Skip buckets we can't access
                    continue
            
            return buckets
            
        except Exception as e:
            self.logger.error(f"Failed to discover S3 buckets in {region}: {str(e)}")
            return []
```

## Extending Reporters

### Base Reporter Class

All reporters inherit from `BaseReporter`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from aws_cis_assessment.core.models import AssessmentResult, ComplianceSummary

class BaseReporter(ABC):
    """Base class for all report generators."""
    
    @abstractmethod
    def generate_report(self, assessment_result: AssessmentResult, 
                       compliance_summary: ComplianceSummary,
                       output_path: str) -> str:
        """Generate report and return content."""
        pass
    
    def _format_compliance_percentage(self, percentage: float) -> str:
        """Format compliance percentage consistently."""
        return f"{percentage:.1f}%"
    
    def _get_compliance_status_color(self, percentage: float) -> str:
        """Get color code for compliance percentage."""
        if percentage >= 90:
            return "green"
        elif percentage >= 70:
            return "yellow"
        else:
            return "red"
```

### Custom Reporter Example

```python
class XMLReporter(BaseReporter):
    """Generate XML format reports."""
    
    def generate_report(self, assessment_result: AssessmentResult, 
                       compliance_summary: ComplianceSummary,
                       output_path: str) -> str:
        """Generate XML report."""
        
        xml_content = self._build_xml_content(assessment_result, compliance_summary)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        return xml_content
    
    def _build_xml_content(self, assessment_result: AssessmentResult, 
                          compliance_summary: ComplianceSummary) -> str:
        """Build XML content."""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom
        
        # Root element
        root = Element('cis_assessment_report')
        root.set('version', '1.0')
        root.set('timestamp', assessment_result.timestamp.isoformat())
        
        # Metadata
        metadata = SubElement(root, 'metadata')
        SubElement(metadata, 'account_id').text = assessment_result.account_id
        SubElement(metadata, 'regions').text = ','.join(assessment_result.regions_assessed)
        SubElement(metadata, 'duration').text = str(assessment_result.assessment_duration)
        
        # Compliance summary
        summary = SubElement(root, 'compliance_summary')
        SubElement(summary, 'overall_compliance').text = str(compliance_summary.overall_compliance_percentage)
        SubElement(summary, 'ig1_compliance').text = str(compliance_summary.ig1_compliance_percentage)
        SubElement(summary, 'ig2_compliance').text = str(compliance_summary.ig2_compliance_percentage)
        SubElement(summary, 'ig3_compliance').text = str(compliance_summary.ig3_compliance_percentage)
        
        # Detailed results
        results = SubElement(root, 'detailed_results')
        
        for ig_name, ig_score in assessment_result.ig_scores.items():
            ig_element = SubElement(results, 'implementation_group')
            ig_element.set('name', ig_name)
            ig_element.set('compliance', f"{ig_score.compliance_percentage:.1f}")
            
            for control_id, control_score in ig_score.control_scores.items():
                control_element = SubElement(ig_element, 'control')
                control_element.set('id', control_id)
                control_element.set('compliance', f"{control_score.compliance_percentage:.1f}")
                
                # Add findings
                for finding in control_score.findings:
                    finding_element = SubElement(control_element, 'finding')
                    finding_element.set('resource_id', finding.resource_id)
                    finding_element.set('status', finding.compliance_status)
                    finding_element.text = finding.evaluation_reason
        
        # Pretty print XML
        rough_string = tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
```

## Testing Framework

### Unit Tests

Use pytest for unit testing:

```python
# tests/test_custom_assessment.py
import pytest
from unittest.mock import Mock, patch
from aws_cis_assessment.controls.custom.custom_s3_assessment import CustomS3BucketAssessment

class TestCustomS3BucketAssessment:
    
    def setup_method(self):
        self.assessment = CustomS3BucketAssessment()
        self.mock_aws_factory = Mock()
    
    @pytest.fixture
    def mock_s3_client(self):
        mock_client = Mock()
        self.mock_aws_factory.get_client.return_value = mock_client
        return mock_client
    
    def test_compliant_bucket(self, mock_s3_client):
        """Test bucket with encryption and versioning enabled."""
        # Mock responses
        mock_s3_client.get_bucket_encryption.return_value = {
            'ServerSideEncryptionConfiguration': {
                'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}]
            }
        }
        mock_s3_client.get_bucket_versioning.return_value = {'Status': 'Enabled'}
        
        resource = {'Name': 'test-bucket', 'Region': 'us-east-1'}
        
        result = self.assessment._evaluate_resource_compliance(resource, self.mock_aws_factory)
        
        assert result.compliance_status == 'COMPLIANT'
        assert result.resource_id == 'test-bucket'
        assert 'encryption and versioning enabled' in result.evaluation_reason
    
    def test_non_compliant_bucket(self, mock_s3_client):
        """Test bucket missing encryption."""
        # Mock responses
        mock_s3_client.get_bucket_encryption.side_effect = Exception("No encryption")
        mock_s3_client.get_bucket_versioning.return_value = {'Status': 'Enabled'}
        
        resource = {'Name': 'test-bucket', 'Region': 'us-east-1'}
        
        result = self.assessment._evaluate_resource_compliance(resource, self.mock_aws_factory)
        
        assert result.compliance_status == 'NON_COMPLIANT'
        assert 'encryption disabled' in result.evaluation_reason
```

### Property-Based Tests

Use Hypothesis for property-based testing:

```python
# tests/test_assessment_properties.py
from hypothesis import given, strategies as st
from aws_cis_assessment.core.scoring_engine import ScoringEngine
from aws_cis_assessment.core.models import ComplianceResult

class TestAssessmentProperties:
    
    @given(st.lists(st.sampled_from(['COMPLIANT', 'NON_COMPLIANT']), min_size=1))
    def test_compliance_percentage_bounds(self, statuses):
        """Property: Compliance percentage should always be between 0 and 100."""
        # Create mock compliance results
        results = []
        for i, status in enumerate(statuses):
            result = ComplianceResult(
                resource_id=f"resource-{i}",
                resource_type="AWS::Test::Resource",
                compliance_status=status,
                evaluation_reason="Test",
                config_rule_name="test-rule",
                region="us-east-1",
                timestamp=datetime.now()
            )
            results.append(result)
        
        scoring_engine = ScoringEngine()
        control_score = scoring_engine.calculate_control_score(results)
        
        assert 0 <= control_score.compliance_percentage <= 100
    
    @given(st.integers(min_value=1, max_value=100))
    def test_all_compliant_gives_100_percent(self, num_resources):
        """Property: All compliant resources should give 100% compliance."""
        results = []
        for i in range(num_resources):
            result = ComplianceResult(
                resource_id=f"resource-{i}",
                resource_type="AWS::Test::Resource",
                compliance_status="COMPLIANT",
                evaluation_reason="Test",
                config_rule_name="test-rule",
                region="us-east-1",
                timestamp=datetime.now()
            )
            results.append(result)
        
        scoring_engine = ScoringEngine()
        control_score = scoring_engine.calculate_control_score(results)
        
        assert control_score.compliance_percentage == 100.0
```

### Integration Tests

Test complete workflows:

```python
# tests/test_integration.py
import pytest
from aws_cis_assessment.core.assessment_engine import AssessmentEngine

@pytest.mark.integration
class TestAssessmentIntegration:
    
    def test_full_ig1_assessment(self, aws_credentials, test_region):
        """Integration test for full IG1 assessment."""
        engine = AssessmentEngine(
            aws_credentials=aws_credentials,
            regions=[test_region],
            max_workers=1
        )
        
        result = engine.run_assessment(implementation_groups=['IG1'])
        
        assert result is not None
        assert result.account_id is not None
        assert len(result.regions_assessed) == 1
        assert 'IG1' in result.ig_scores
        assert result.total_resources_evaluated > 0
```

## Contributing Guidelines

### Code Standards

1. **Follow PEP 8**: Use black for formatting
2. **Type hints**: Add type hints to all functions
3. **Docstrings**: Use Google-style docstrings
4. **Error handling**: Handle exceptions gracefully
5. **Logging**: Use structured logging

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-control`
3. **Write tests**: Ensure good test coverage
4. **Update documentation**: Update relevant docs
5. **Run quality checks**: `pre-commit run --all-files`
6. **Submit PR**: Include description and testing notes

### Testing Requirements

- **Unit tests**: Test individual components
- **Integration tests**: Test complete workflows
- **Property tests**: Test invariants and properties
- **Coverage**: Maintain >90% test coverage

### Documentation Requirements

- **Code comments**: Explain complex logic
- **API documentation**: Document all public APIs
- **User documentation**: Update user guides
- **Examples**: Provide usage examples

## API Reference

### Core Classes

#### AssessmentEngine

Main orchestration class for running assessments.

```python
class AssessmentEngine:
    def __init__(self, aws_credentials: Dict[str, str], regions: List[str], 
                 config_path: Optional[str] = None, max_workers: int = 4):
        """Initialize assessment engine."""
    
    def run_assessment(self, implementation_groups: Optional[List[str]] = None,
                      controls: Optional[List[str]] = None) -> AssessmentResult:
        """Run compliance assessment."""
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return errors."""
```

#### ScoringEngine

Calculate compliance scores from assessment results.

```python
class ScoringEngine:
    def calculate_control_score(self, results: List[ComplianceResult]) -> ControlScore:
        """Calculate compliance score for individual control."""
    
    def calculate_ig_score(self, control_scores: Dict[str, ControlScore]) -> IGScore:
        """Calculate Implementation Group compliance score."""
    
    def generate_compliance_summary(self, assessment_result: AssessmentResult) -> ComplianceSummary:
        """Generate executive summary of compliance status."""
```

#### AWSClientFactory

Manage AWS service clients with credential handling.

```python
class AWSClientFactory:
    def __init__(self, credentials: Dict[str, str], regions: List[str]):
        """Initialize with AWS credentials and regions."""
    
    def get_client(self, service_name: str, region: str = None) -> boto3.client:
        """Get AWS service client for specified service and region."""
    
    def validate_credentials(self) -> bool:
        """Validate AWS credentials and permissions."""
```

### Data Models

All data models are defined in `aws_cis_assessment.core.models`:

- `ComplianceResult`: Individual resource compliance result
- `ControlScore`: CIS Control compliance score
- `IGScore`: Implementation Group compliance score
- `AssessmentResult`: Complete assessment result
- `ComplianceSummary`: Executive summary

### Utility Functions

Common utility functions are available in various modules:

- `aws_cis_assessment.cli.utils`: CLI utilities
- `aws_cis_assessment.core.utils`: Core utilities
- `aws_cis_assessment.reporters.utils`: Reporting utilities