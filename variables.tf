variable "RESOURCE_GROUP_NAME" {
  type = string
  default = "Az-Resume"
}

variable "LOCATION" {
  type = string
  default = "East US"
}

variable "STORAGE_ACCOUNT_NAME" {
  type = string
  default = "jpolanskyresume"
}

variable "DOMAIN_NAME" {
  type = string
  default = "jon-polansky.com"
}

variable "EMAIL_ADDRESS" {
  type = string
  default = "jon@jon-polansky.com"
}

variable "CLOUDFLARE_API_TOKEN" {
  type = string
}

variable "CLOUDFLARE_ZONE_ID" {
  type = string
}

variable "COSMOSDB_ACCOUNT_NAME" {
  type = string
  default = "resumedb1"
}

variable "SENDGRID_API_KEY" {
  type = string
}