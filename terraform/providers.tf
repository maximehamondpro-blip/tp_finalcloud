terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  assume_role {
    role_arn = "arn:aws:iam::738563260931:role/role_etudiants"
  }

  default_tags {
    tags = {
      Project = "ynov-iac-2025"
    }
  }
}
