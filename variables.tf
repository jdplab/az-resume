variable "TF_WORKSPACE_NAME" {
    type = string
    default = "azure-resume"
}

variable "RESOURCE_GROUP_NAME" {
    type = string
    default = "Resume"
}

variable "LOCATION" {
    type = string
    default = "East US"
}

variable "STORAGE_ACCOUNT_NAME" {
  type = string
  default = "resumestorage"
}