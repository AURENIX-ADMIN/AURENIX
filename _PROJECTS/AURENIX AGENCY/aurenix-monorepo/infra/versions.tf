terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    temporalcloud = {
      source  = "temporalio/temporalcloud"
      version = "~> 0.4"
    }
  }
}

provider "google" {
  # Configuration via environment variables or gcloud auth
}

provider "temporalcloud" {
  # Configuration via environment variables
}
