terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.16.0"
    }
  }
}

provider "google" {
  project = var.project_name
  credentials = file(var.credentials)
  region = var.region
}

resource "google_storage_bucket" "job_pipeline_data" {
  name = var.name
  location = var.region
  force_destroy = true
}