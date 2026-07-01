terraform {
  backend "s3" {
    bucket = "ynov-iac-2025-tfstate-mh"
    key    = "terraform.tfstate"
    region = "eu-west-3"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project = "ynov-iac-2025"
    }
  }
}
