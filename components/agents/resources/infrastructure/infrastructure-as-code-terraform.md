# Infrastructure as Code - Terraform

Comprehensive guide to Infrastructure as Code implementation using Terraform, including best practices, module design, and multi-environment management.

## 📑 Table of Contents

- [Terraform Best Practices](#terraform-best-practices)
  - [Project Structure](#project-structure)
  - [State Management](#state-management)
  - [Version Pinning](#version-pinning)
  - [Code Organization](#code-organization)
- [Module Design Patterns](#module-design-patterns)
  - [Module Structure](#module-structure)
  - [Module Composition](#module-composition)
  - [Module Registry](#module-registry)
- [Workspaces and Environments](#workspaces-and-environments)
  - [Workspace Strategy](#workspace-strategy)
  - [Directory-Based Environments](#directory-based-environments)
- [Multi-Environment Management](#multi-environment-management)
  - [Environment-Specific Variables](#environment-specific-variables)
  - [Promotion Strategy](#promotion-strategy)
- [CI/CD Integration](#cicd-integration)
  - [Automated Terraform Pipeline](#automated-terraform-pipeline)
  - [Terraform Testing](#terraform-testing)
- [Advanced Patterns](#advanced-patterns)
  - [Dynamic Blocks](#dynamic-blocks)
  - [Conditional Resources](#conditional-resources)
  - [For Expressions](#for-expressions)
  - [Sensitive Data Handling](#sensitive-data-handling)

---

## Terraform Best Practices

### Project Structure

**Recommended Directory Layout**
```
terraform-infrastructure/
├── modules/                    # Reusable modules
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── eks-cluster/
│   ├── rds-postgres/
│   └── s3-bucket/
├── environments/               # Environment-specific configs
│   ├── production/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   └── development/
├── global/                     # Shared resources (IAM, Route53)
│   ├── iam/
│   └── dns/
└── README.md
```

### State Management

**Remote State Configuration**
```hcl
# backend.tf - S3 backend with DynamoDB locking
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "production/eks-cluster/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"

    # Optional: State encryption with KMS
    kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/abc123"
  }
}
```

**State Backend Best Practices**
- Use remote backend (S3, Azure Storage, GCS) for team collaboration
- Enable state locking (DynamoDB for S3) to prevent concurrent modifications
- Encrypt state files (contain sensitive data)
- Enable versioning on state bucket for recovery
- Restrict access to state bucket (contains secrets)
- Separate state files by environment and component

**State Management Commands**
```bash
# List resources in state
terraform state list

# Show specific resource
terraform state show aws_instance.web

# Move resource to different state file
terraform state mv aws_instance.web module.web.aws_instance.main

# Remove resource from state (doesn't destroy)
terraform state rm aws_instance.old

# Import existing resource into state
terraform import aws_instance.web i-1234567890abcdef
```

### Version Pinning

**Terraform Version Constraints**
```hcl
terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Any 5.x version
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.20.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}
```

**Version Pinning Strategies**
- Pin major version for stability (`~> 5.0` allows 5.x updates)
- Test upgrades in non-production first
- Use `.terraform.lock.hcl` for exact provider versions
- Document upgrade procedures in README
- Subscribe to provider changelogs for breaking changes

### Code Organization

**File Structure**
- `main.tf`: Primary resource definitions
- `variables.tf`: Input variable declarations
- `outputs.tf`: Output value definitions
- `locals.tf`: Local values and computed values
- `data.tf`: Data source definitions
- `versions.tf`: Terraform and provider version constraints
- `backend.tf`: Remote state backend configuration

**Naming Conventions**
- Use lowercase and hyphens for resources: `aws_instance.web-server`
- Descriptive names: `aws_security_group.web_server_sg` not `aws_security_group.sg1`
- Prefix resources with type: `var.vpc_cidr` not `var.cidr`
- Use consistent naming across modules

## Module Design Patterns

### Module Structure

**Well-Designed Module**
```
modules/vpc/
├── main.tf           # Resource definitions
├── variables.tf      # Input variables with descriptions and validation
├── outputs.tf        # Exported values for other modules
├── README.md         # Usage documentation and examples
├── versions.tf       # Provider version constraints
└── examples/         # Example usage
    └── complete/
        ├── main.tf
        └── variables.tf
```

**Module Variables**
```hcl
# variables.tf
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "Must be a valid CIDR block."
  }
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string

  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "availability_zones" {
  description = "List of availability zones for subnet creation"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
```

**Module Outputs**
```hcl
# outputs.tf
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "nat_gateway_ips" {
  description = "Elastic IPs of NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}
```

### Module Composition

**Using Modules**
```hcl
# environments/production/main.tf
module "vpc" {
  source = "../../modules/vpc"

  vpc_cidr           = "10.0.0.0/16"
  environment        = "production"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
    CostCenter  = "Infrastructure"
  }
}

module "eks_cluster" {
  source = "../../modules/eks-cluster"

  cluster_name       = "production-eks"
  cluster_version    = "1.27"
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids

  node_groups = {
    general = {
      desired_size = 3
      min_size     = 2
      max_size     = 10
      instance_types = ["m5.large", "m5a.large"]
    }
  }

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}

module "rds_postgres" {
  source = "../../modules/rds-postgres"

  identifier         = "production-db"
  engine_version     = "15.3"
  instance_class     = "db.r6g.xlarge"
  allocated_storage  = 100

  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  allowed_cidr_blocks = module.vpc.private_subnet_cidrs

  backup_retention_period = 7
  multi_az               = true

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}
```

### Module Registry

**Using Public Modules**
```hcl
# Use official AWS VPC module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.0"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false  # One NAT per AZ for HA

  tags = {
    Environment = "production"
  }
}
```

**Publishing Private Modules**
- Use Git tags for versioning (`v1.0.0`, `v1.1.0`)
- Terraform Cloud/Enterprise private registry
- Document inputs, outputs, and examples
- Include CI/CD validation (terraform validate, tflint, tfsec)

## Workspaces and Environments

### Workspace Strategy

**Using Workspaces**
```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new staging

# Switch workspace
terraform workspace select production

# Show current workspace
terraform workspace show
```

**Workspace-Aware Configuration**
```hcl
locals {
  environment = terraform.workspace

  instance_count = {
    production  = 5
    staging     = 2
    development = 1
  }

  instance_type = {
    production  = "m5.large"
    staging     = "t3.medium"
    development = "t3.small"
  }
}

resource "aws_instance" "app" {
  count         = local.instance_count[local.environment]
  instance_type = local.instance_type[local.environment]

  tags = {
    Environment = local.environment
  }
}
```

**Workspace Limitations**
- All workspaces share same backend configuration
- Can't have different providers per workspace
- State files grow with number of workspaces
- Better for simple environment separation

### Directory-Based Environments

**Separate Directories (Recommended for Production)**
```
environments/
├── production/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── backend.tf
├── staging/
│   ├── main.tf
│   ├── variables.tf
│   ├── terraform.tfvars
│   └── backend.tf
└── development/
    ├── main.tf
    ├── variables.tf
    ├── terraform.tfvars
    └── backend.tf
```

**Benefits**
- Complete isolation between environments
- Different backends per environment
- Different provider configurations
- Easier access control (different AWS accounts)
- Reduced blast radius (staging changes don't risk production)

## Multi-Environment Management

### Environment-Specific Variables

**terraform.tfvars Files**
```hcl
# environments/production/terraform.tfvars
environment = "production"
region      = "us-east-1"

vpc_cidr = "10.0.0.0/16"

eks_cluster_version = "1.27"
eks_node_groups = {
  general = {
    desired_size   = 5
    min_size       = 3
    max_size       = 20
    instance_types = ["m5.xlarge", "m5a.xlarge"]
  }
  spot = {
    desired_size   = 3
    min_size       = 0
    max_size       = 10
    instance_types = ["m5.large", "m5a.large", "m4.large"]
    capacity_type  = "SPOT"
  }
}

rds_instance_class      = "db.r6g.2xlarge"
rds_backup_retention    = 7
rds_multi_az            = true
rds_deletion_protection = true
```

**Variable Precedence**
1. Command-line flags: `-var="key=value"`
2. `*.auto.tfvars` files (alphabetical order)
3. `terraform.tfvars` file
4. Environment variables: `TF_VAR_name`
5. Default values in variable declarations

### Promotion Strategy

**Git-Based Promotion**
```bash
# 1. Develop in feature branch
git checkout -b feature/add-redis

# 2. Test in development environment
cd environments/development
terraform plan
terraform apply

# 3. Merge to main, deploy to staging
git checkout main
git merge feature/add-redis
cd environments/staging
terraform plan
terraform apply

# 4. Tag release, deploy to production
git tag v1.5.0
cd environments/production
terraform plan
terraform apply
```

**Terragrunt for DRY Configuration**
```hcl
# terragrunt.hcl - Root configuration
remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite"
  }
  config = {
    bucket         = "company-terraform-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# environments/production/terragrunt.hcl
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../modules//vpc"
}

inputs = {
  environment = "production"
  vpc_cidr    = "10.0.0.0/16"
}
```

## CI/CD Integration

### Automated Terraform Pipeline

**GitHub Actions Workflow**
```yaml
name: Terraform CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  TF_VERSION: 1.5.7

jobs:
  terraform-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init -backend=false
        working-directory: environments/production

      - name: Terraform Validate
        run: terraform validate
        working-directory: environments/production

      - name: TFLint
        uses: terraform-linters/setup-tflint@v3
      - run: tflint --init
      - run: tflint --recursive

      - name: TFSec Security Scan
        uses: aquasecurity/tfsec-action@v1.0.0

  terraform-plan:
    needs: terraform-validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActions
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Init
        run: terraform init
        working-directory: environments/staging

      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: environments/staging

      - name: Comment PR with Plan
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('environments/staging/tfplan.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Terraform Plan\n\`\`\`\n${plan}\n\`\`\``
            });

  terraform-apply:
    needs: terraform-validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActions
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Init
        run: terraform init
        working-directory: environments/staging

      - name: Terraform Apply
        run: terraform apply -auto-approve
        working-directory: environments/staging
```

### Terraform Testing

**Terratest (Go)**
```go
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCModule(t *testing.T) {
    terraformOptions := &terraform.Options{
        TerraformDir: "../examples/complete",
        Vars: map[string]interface{}{
            "vpc_cidr":     "10.0.0.0/16",
            "environment":  "test",
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)

    privateSubnets := terraform.OutputList(t, terraformOptions, "private_subnet_ids")
    assert.Equal(t, 3, len(privateSubnets))
}
```

**TFLint Configuration**
```hcl
# .tflint.hcl
plugin "aws" {
  enabled = true
  version = "0.25.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

rule "aws_instance_invalid_type" {
  enabled = true
}

rule "aws_instance_previous_type" {
  enabled = true
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}
```

## Advanced Patterns

### Dynamic Blocks

**Dynamic Security Group Rules**
```hcl
variable "ingress_rules" {
  type = list(object({
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
    description = string
  }))
  default = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTPS from internet"
    },
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "HTTP from internet"
    }
  ]
}

resource "aws_security_group" "web" {
  name        = "web-sg"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.from_port
      to_port     = ingress.value.to_port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
      description = ingress.value.description
    }
  }
}
```

### Conditional Resources

**Create Resources Based on Conditions**
```hcl
variable "enable_monitoring" {
  type    = bool
  default = true
}

variable "environment" {
  type = string
}

resource "aws_cloudwatch_dashboard" "main" {
  count = var.enable_monitoring ? 1 : 0

  dashboard_name = "${var.environment}-dashboard"
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization"]
          ]
        }
      }
    ]
  })
}

# Production-only resources
resource "aws_backup_plan" "production" {
  count = var.environment == "production" ? 1 : 0

  name = "production-backup-plan"

  rule {
    rule_name         = "daily_backup"
    target_vault_name = aws_backup_vault.main[0].name
    schedule          = "cron(0 2 * * ? *)"

    lifecycle {
      delete_after = 30
    }
  }
}
```

### For Expressions

**Transform Lists and Maps**
```hcl
variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

locals {
  # Create subnet CIDR for each AZ
  private_subnets = [
    for idx, az in var.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, idx)
  ]

  # Create map of AZ to subnet
  az_subnet_map = {
    for idx, az in var.availability_zones :
    az => cidrsubnet(var.vpc_cidr, 8, idx)
  }

  # Filter production tags
  production_tags = {
    for k, v in var.tags :
    k => v
    if var.environment == "production"
  }
}
```

### Sensitive Data Handling

**Protecting Sensitive Outputs**
```hcl
output "database_password" {
  description = "Database administrator password"
  value       = aws_db_instance.main.password
  sensitive   = true
}

output "api_key" {
  description = "API key for external service"
  value       = random_password.api_key.result
  sensitive   = true
}
```

**Using External Secrets**
```hcl
# Retrieve secret from AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "production/database/password"
}

resource "aws_db_instance" "main" {
  identifier = "production-db"
  password   = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["password"]

  # Other configuration...
}
```
