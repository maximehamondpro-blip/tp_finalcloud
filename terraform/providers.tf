terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
provider "aws" {
  region = var.aws_region
  default_tags { tags = { Project = "ynov-iac-2025" } }

  assume_role {
    role_arn     = "arn:aws:iam::738563260931:role/role_etudiants"
    session_name = "tp-final-mh"
  }
}
