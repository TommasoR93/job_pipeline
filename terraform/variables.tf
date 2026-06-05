variable "project_name" {
    description = "Project Name is same as projectID defined in GCP"
}

variable "credentials" {
    description = "Keys to the service account created in GCP"
}

variable "region" {
    description = "Region where the service is set up"
}

variable "name" {
    description = "Bucket name in GCP"
}
