# Config Rule Mappings

This document provides a comprehensive mapping of CIS Controls to AWS Config rules used by the assessment tool.

## Table of Contents

1. [Overview](#overview)
2. [IG1 - Essential Cyber Hygiene](#ig1---essential-cyber-hygiene)
3. [IG2 - Enhanced Security](#ig2---enhanced-security)
4. [IG3 - Advanced Security](#ig3---advanced-security)
5. [Config Rule Details](#config-rule-details)
6. [Resource Type Coverage](#resource-type-coverage)
7. [Assessment Logic](#assessment-logic)

## Overview

The AWS CIS Controls Compliance Assessment Tool uses AWS Config rule specifications as the foundation for evaluating compliance. Each CIS Control is mapped to one or more AWS Config rules that assess specific AWS resources and configurations.

### Mapping Methodology

1. **Direct Mapping**: CIS Controls directly correspond to existing AWS Config rules
2. **Composite Mapping**: Multiple Config rules combine to assess a single CIS Control
3. **Custom Logic**: Additional assessment logic based on Config rule specifications
4. **Resource Coverage**: All applicable AWS resource types are evaluated

### Implementation Groups Hierarchy

- **IG1**: 56 Config rules covering essential cyber hygiene
- **IG2**: +30 Config rules for enhanced security (includes all IG1 rules)
- **IG3**: +20 Config rules for advanced security (includes all IG1+IG2 rules)

## IG1 - Essential Cyber Hygiene

### Control 1.1: Establish and Maintain Detailed Enterprise Asset Inventory

**Purpose**: Maintain an accurate and up-to-date inventory of all enterprise assets.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `eip-attached` | AWS::EC2::EIP | Ensures Elastic IPs are attached to EC2 instances or ENIs |
| `ec2-stopped-instance` | AWS::EC2::Instance | Checks for EC2 instances stopped for more than allowed days |
| `vpc-network-acl-unused-check` | AWS::EC2::NetworkAcl | Ensures VPC network ACLs are in use |
| `ec2-instance-managed-by-systems-manager` | AWS::EC2::Instance, AWS::SSM::ManagedInstanceInventory | Ensures EC2 instances are managed by Systems Manager |
| `ec2-security-group-attached-to-eni` | AWS::EC2::SecurityGroup | Ensures security groups are attached to network interfaces |

**Assessment Logic**:
- Discovers all EC2 instances, EIPs, security groups, and network ACLs
- Validates that resources are properly managed and not orphaned
- Checks Systems Manager agent installation and registration

### Control 2.2: Ensure Authorized Software is Currently Supported

**Purpose**: Ensure that only authorized and supported software is installed and running.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `elastic-beanstalk-managed-updates-enabled` | AWS::ElasticBeanstalk::Environment | Ensures Elastic Beanstalk environments have managed updates enabled |
| `lambda-function-settings-check` | AWS::Lambda::Function | Validates Lambda function runtime and configuration settings |
| `ec2-imdsv2-check` | AWS::EC2::Instance | Ensures EC2 instances use IMDSv2 for metadata access |

**Assessment Logic**:
- Validates that compute services use supported and current software versions
- Checks for automatic update mechanisms where available
- Ensures secure configuration of runtime environments

### Control 3.3: Configure Data Access Control Lists

**Purpose**: Configure data access control lists on network shares and databases.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `iam-password-policy` | AWS::IAM::AccountPasswordPolicy | Ensures IAM password policy meets security requirements |
| `iam-user-mfa-enabled` | AWS::IAM::User | Ensures IAM users have MFA enabled |
| `iam-root-access-key-check` | AWS::IAM::User | Ensures root account access keys are not present |
| `s3-bucket-public-read-prohibited` | AWS::S3::Bucket | Ensures S3 buckets do not allow public read access |
| `s3-bucket-public-write-prohibited` | AWS::S3::Bucket | Ensures S3 buckets do not allow public write access |
| `ec2-instance-no-public-ip` | AWS::EC2::Instance | Ensures EC2 instances do not have public IP addresses |
| `rds-instance-public-access-check` | AWS::RDS::DBInstance | Ensures RDS instances are not publicly accessible |
| `redshift-cluster-public-access-check` | AWS::Redshift::Cluster | Ensures Redshift clusters are not publicly accessible |
| `dms-replication-not-public` | AWS::DMS::ReplicationInstance | Ensures DMS replication instances are not public |
| `ec2-instance-profile-attached` | AWS::EC2::Instance | Ensures EC2 instances have IAM instance profiles attached |

**Assessment Logic**:
- Evaluates IAM policies and access controls
- Checks for public accessibility of data stores
- Validates proper authentication and authorization mechanisms

### Control 4.1: Establish and Maintain a Secure Configuration Process

**Purpose**: Establish and maintain a secure configuration process for enterprise assets.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `account-part-of-organizations` | AWS::Organizations::Account | Ensures AWS account is part of AWS Organizations |
| `ec2-volume-inuse-check` | AWS::EC2::Volume | Ensures EBS volumes are attached to EC2 instances |
| `redshift-cluster-maintenancesettings-check` | AWS::Redshift::Cluster | Validates Redshift cluster maintenance settings |
| `secretsmanager-rotation-enabled-check` | AWS::SecretsManager::Secret | Ensures Secrets Manager secrets have rotation enabled |
| `rds-automatic-minor-version-upgrade-enabled` | AWS::RDS::DBInstance | Ensures RDS instances have automatic minor version upgrades |

**Assessment Logic**:
- Validates organizational governance structures
- Checks for proper resource utilization and maintenance
- Ensures automatic security updates and rotation policies

### Control 5.2: Use Unique Passwords

**Purpose**: Use unique passwords for all enterprise assets.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `iam-password-policy` | AWS::IAM::AccountPasswordPolicy | Enhanced password policy validation |
| `mfa-enabled-for-iam-console-access` | AWS::IAM::User | Ensures MFA is enabled for console access |
| `root-account-mfa-enabled` | AWS::IAM::User | Ensures root account has MFA enabled |
| `iam-user-unused-credentials-check` | AWS::IAM::User | Identifies unused IAM user credentials |

**Assessment Logic**:
- Validates password complexity requirements
- Checks for MFA enforcement
- Identifies stale or unused credentials

## IG2 - Enhanced Security

### Control 3.10: Encrypt Sensitive Data in Transit

**Purpose**: Encrypt sensitive data in transit between network locations.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `api-gw-ssl-enabled` | AWS::ApiGateway::Stage | Ensures API Gateway stages use SSL/TLS |
| `alb-http-to-https-redirection-check` | AWS::ElasticLoadBalancingV2::LoadBalancer | Ensures ALB redirects HTTP to HTTPS |
| `elb-tls-https-listeners-only` | AWS::ElasticLoadBalancing::LoadBalancer | Ensures ELB uses only TLS/HTTPS listeners |
| `s3-bucket-ssl-requests-only` | AWS::S3::Bucket | Ensures S3 buckets require SSL requests |
| `redshift-require-tls-ssl` | AWS::Redshift::Cluster | Ensures Redshift requires TLS/SSL connections |
| `elasticsearch-https-required` | AWS::Elasticsearch::Domain | Ensures Elasticsearch domains require HTTPS |
| `cloudfront-viewer-policy-https` | AWS::CloudFront::Distribution | Ensures CloudFront uses HTTPS viewer policy |

**Assessment Logic**:
- Validates SSL/TLS configuration across all services
- Checks for proper certificate management
- Ensures encryption in transit for data flows

### Control 3.11: Encrypt Sensitive Data at Rest

**Purpose**: Encrypt sensitive data at rest on all enterprise assets.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `encrypted-volumes` | AWS::EC2::Volume | Ensures EBS volumes are encrypted |
| `rds-storage-encrypted` | AWS::RDS::DBInstance | Ensures RDS instances have encrypted storage |
| `s3-default-encryption-kms` | AWS::S3::Bucket | Ensures S3 buckets have default KMS encryption |
| `dynamodb-table-encrypted-kms` | AWS::DynamoDB::Table | Ensures DynamoDB tables are encrypted with KMS |
| `backup-recovery-point-encrypted` | AWS::Backup::RecoveryPoint | Ensures backup recovery points are encrypted |
| `elasticsearch-encrypted-at-rest` | AWS::Elasticsearch::Domain | Ensures Elasticsearch domains are encrypted at rest |
| `redshift-cluster-kms-enabled` | AWS::Redshift::Cluster | Ensures Redshift clusters use KMS encryption |
| `secretsmanager-secret-encrypted-with-kms-key` | AWS::SecretsManager::Secret | Ensures secrets are encrypted with KMS |

**Assessment Logic**:
- Validates encryption configuration for all data stores
- Checks for proper KMS key usage
- Ensures encryption at rest for backups and snapshots

### Control 7.1: Establish and Maintain a Vulnerability Management Process

**Purpose**: Establish and maintain a vulnerability management process.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `ecr-private-image-scanning-enabled` | AWS::ECR::Repository | Ensures ECR repositories have image scanning enabled |
| `guardduty-enabled-centralized` | AWS::GuardDuty::Detector | Ensures GuardDuty is enabled and centralized |
| `ec2-managedinstance-patch-compliance-status-check` | AWS::EC2::Instance | Ensures EC2 instances are compliant with patch management |
| `inspector-assessment-target-exists` | AWS::Inspector::AssessmentTarget | Ensures Inspector assessment targets exist |

**Assessment Logic**:
- Validates vulnerability scanning capabilities
- Checks for threat detection services
- Ensures patch management compliance

## IG3 - Advanced Security

### Control 3.14: Log Sensitive Data Access

**Purpose**: Log sensitive data access including modification and disposal.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `api-gw-execution-logging-enabled` | AWS::ApiGateway::Stage | Ensures API Gateway execution logging is enabled |
| `cloudtrail-s3-dataevents-enabled` | AWS::CloudTrail::Trail | Ensures CloudTrail logs S3 data events |
| `multi-region-cloudtrail-enabled` | AWS::CloudTrail::Trail | Ensures multi-region CloudTrail is enabled |
| `cloud-trail-cloud-watch-logs-enabled` | AWS::CloudTrail::Trail | Ensures CloudTrail sends logs to CloudWatch |
| `s3-bucket-logging-enabled` | AWS::S3::Bucket | Ensures S3 bucket access logging is enabled |
| `vpc-flow-logs-enabled` | AWS::EC2::VPC | Ensures VPC Flow Logs are enabled |

**Assessment Logic**:
- Validates comprehensive logging configuration
- Checks for data access event logging
- Ensures log centralization and retention

### Control 12.8: Establish and Maintain Network Segmentation

**Purpose**: Establish and maintain network segmentation for all enterprise assets.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `api-gw-associated-with-waf` | AWS::ApiGateway::Stage | Ensures API Gateway is associated with WAF |
| `vpc-sg-open-only-to-authorized-ports` | AWS::EC2::SecurityGroup | Ensures security groups open only authorized ports |
| `no-unrestricted-route-to-igw` | AWS::EC2::RouteTable | Ensures no unrestricted routes to Internet Gateway |
| `subnet-auto-assign-public-ip-disabled` | AWS::EC2::Subnet | Ensures subnets don't auto-assign public IPs |
| `nacl-no-unrestricted-ssh-rdp` | AWS::EC2::NetworkAcl | Ensures NACLs don't allow unrestricted SSH/RDP |

**Assessment Logic**:
- Validates network segmentation controls
- Checks for proper firewall configurations
- Ensures restricted network access patterns

### Control 13.1: Centralize Security Event Alerting

**Purpose**: Centralize security event alerting across the enterprise.

| Config Rule | Resource Types | Description |
|-------------|----------------|-------------|
| `restricted-incoming-traffic` | AWS::EC2::SecurityGroup | Ensures security groups restrict incoming traffic |
| `incoming-ssh-disabled` | AWS::EC2::SecurityGroup | Ensures SSH access is properly restricted |
| `guardduty-non-archived-findings` | AWS::GuardDuty::Detector | Ensures GuardDuty findings are not archived |
| `securityhub-enabled` | AWS::SecurityHub::Hub | Ensures Security Hub is enabled for centralization |

**Assessment Logic**:
- Validates centralized security monitoring
- Checks for proper alerting mechanisms
- Ensures security event correlation

## Config Rule Details

### Rule Parameters

Many Config rules accept parameters that customize their behavior:

```yaml
# Example: IAM Password Policy
iam-password-policy:
  parameters:
    RequireUppercaseCharacters: true
    RequireLowercaseCharacters: true
    RequireNumbers: true
    RequireSymbols: true
    MinimumPasswordLength: 14
    PasswordReusePrevention: 24
    MaxPasswordAge: 90
```

### Evaluation Triggers

Config rules are triggered by:
- **Configuration Changes**: When resource configurations change
- **Periodic**: At regular intervals (24 hours by default)
- **On-Demand**: When manually triggered

### Compliance Status

Each resource evaluation results in one of these statuses:
- **COMPLIANT**: Resource meets the rule requirements
- **NON_COMPLIANT**: Resource violates the rule requirements
- **NOT_APPLICABLE**: Rule doesn't apply to this resource
- **INSUFFICIENT_DATA**: Not enough information to evaluate

## Resource Type Coverage

### Compute Services
- **EC2**: Instances, volumes, security groups, network interfaces
- **Lambda**: Functions, layers, event source mappings
- **Elastic Beanstalk**: Applications, environments

### Storage Services
- **S3**: Buckets, bucket policies, access points
- **EBS**: Volumes, snapshots
- **EFS**: File systems, mount targets

### Database Services
- **RDS**: DB instances, clusters, snapshots
- **DynamoDB**: Tables, global tables
- **Redshift**: Clusters, parameter groups
- **ElastiCache**: Clusters, replication groups

### Networking Services
- **VPC**: VPCs, subnets, route tables, NACLs
- **ELB**: Classic load balancers, application load balancers
- **CloudFront**: Distributions, origins
- **API Gateway**: APIs, stages, deployments

### Security Services
- **IAM**: Users, roles, policies, groups
- **KMS**: Keys, aliases, grants
- **Secrets Manager**: Secrets, rotation configurations
- **GuardDuty**: Detectors, findings
- **Security Hub**: Hubs, standards subscriptions

### Management Services
- **CloudTrail**: Trails, event data stores
- **CloudWatch**: Alarms, log groups, metrics
- **Systems Manager**: Managed instances, patch compliance
- **Organizations**: Accounts, organizational units

## Assessment Logic

### Resource Discovery

For each Config rule, the assessment tool:

1. **Identifies Resource Types**: Determines which AWS resource types to evaluate
2. **Discovers Resources**: Uses AWS APIs to find all resources of the specified types
3. **Filters by Region**: Evaluates resources in the specified regions
4. **Applies Rule Logic**: Executes the Config rule evaluation logic

### Evaluation Process

```python
def evaluate_config_rule(rule_name, resource_type, region):
    # 1. Discover resources
    resources = discover_resources(resource_type, region)
    
    # 2. For each resource
    for resource in resources:
        # 3. Apply rule logic
        compliance_result = apply_rule_logic(rule_name, resource)
        
        # 4. Generate result
        yield ComplianceResult(
            resource_id=resource.id,
            resource_type=resource_type,
            compliance_status=compliance_result.status,
            evaluation_reason=compliance_result.reason,
            config_rule_name=rule_name,
            region=region,
            timestamp=datetime.now()
        )
```

### Scoring Calculation

Compliance scores are calculated as:

```
Control Score = (Compliant Resources / Total Resources) × 100
IG Score = Weighted Average of Control Scores
Overall Score = Weighted Average of IG Scores
```

### Error Handling

The assessment tool handles various error conditions:

- **Permission Errors**: Mark as "INSUFFICIENT_PERMISSIONS"
- **Service Unavailable**: Mark as "ERROR" with details
- **Resource Not Found**: Mark as "NOT_APPLICABLE"
- **API Throttling**: Implement exponential backoff and retry

### Remediation Guidance

Each non-compliant finding includes:

1. **Specific Steps**: Detailed remediation instructions
2. **AWS CLI Commands**: Ready-to-use command examples
3. **Console Links**: Direct links to AWS Console
4. **Documentation**: Links to relevant AWS documentation
5. **Priority**: Risk-based priority (HIGH, MEDIUM, LOW)

This comprehensive mapping ensures that the assessment tool provides accurate, actionable compliance evaluation based on AWS Config rule specifications while maintaining independence from the AWS Config service itself.