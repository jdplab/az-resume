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
  default = "azureresume.jon-polansky.com"
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

variable "COSMOSDB_URI" {
  type = string
  default = "https://resumedb1.documents.azure.com:443/"
}

variable "COSMOSDB_KEY" {
  type = string
}