terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket = "fiap-datalake-tech-terraform"
    region = "us-east-1"
    key = "datalake.tfstate"
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}
