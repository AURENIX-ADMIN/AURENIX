variable "client_slug" {
  description = "Slug for the client, used in project ID"
  type        = string
}

variable "environment" {
  description = "Environment (dev, prod)"
  type        = string
}

variable "client_id" {
  description = "Internal Client ID"
  type        = string
}

variable "billing_account_id" {
  description = "Billing Account ID"
  type        = string
}

variable "org_id" {
  description = "Organization ID"
  type        = string
}
