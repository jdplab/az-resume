terraform {

  backend "remote" {
    organization = "JP-Lab"

    workspaces {
      name = "azure-resume"
    }
  }
}

terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.94.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "resume" {
  name     = var.RESOURCE_GROUP_NAME
  location = var.LOCATION
}

resource "azurerm_storage_account" "resume" {
  name                     = var.STORAGE_ACCOUNT_NAME
  resource_group_name      = azurerm_resource_group.resume.name
  location                 = azurerm_resource_group.resume.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  static_website {
    index_document = "index.html"
  }
}

# resource "azurerm_storage_blob" "resume" {
#   name                   = "index.html"
#   storage_account_name   = azurerm_storage_account.resume.name
#   storage_container_name = "$web"
#   type                   = "Block"
#   content_type           = "text/html"
#   source                 = "index.html"
# }

# resource "azurerm_cdn_profile" "resume" {
#   name     = "resumecdn"
#   location = azurerm_resource_group.resume.location
#   resource_group_name = azurerm_resource_group.resume.name
#   sku {
#     name     = "Standard_Microsoft"
#     tier     = "Standard"
#   }
# }

# resource "azurerm_cdn_endpoint" "resume" {
#   name                = "resumecdnendpoint"
#   profile_name        = azurerm_cdn_profile.resume.name
#   location            = azurerm_resource_group.resume.location
#   resource_group_name = azurerm_resource_group.resume.name
#   origin {
#     name      = azurerm_storage_account.resume.name
#     host_name = azurerm_storage_account.resume.primary_web_endpoint
#   }
# }

# resource "azurerm_cdn_custom_domain" "resume" {
#   name                = "resumecustomdomain"
#   hostname            = "azureresume.jon-polansky.com"
#   profile_name        = azurerm_cdn_profile.resume.name
#   endpoint_name       = azurerm_cdn_endpoint.resume.name
#   resource_group_name = azurerm_resource_group.resume.name
# }

# resource "azurerm_service_plan" "resume" {
#   name                = "resumeserviceplan"
#   location            = azurerm_resource_group.resume.location
#   resource_group_name = azurerm_resource_group.resume.name
#   sku {
#     tier = "Free"
#     size = "F1"
#   }
# }

# resource "azurerm_linux_function_app" "resume" {
#   name                      = "resume-visitorcounter"
#   location                  = azurerm_resource_group.resume.location
#   resource_group_name       = azurerm_resource_group.resume.name
#   app_service_plan_id       = azurerm_service_plan.resume.id
#   storage_account_name      = azurerm_storage_account.resume.name
#   storage_account_access_key = azurerm_storage_account.resume.primary_access_key
#   app_settings = {
#     "WEBSITE_RUN_FROM_PACKAGE" = azurerm_storage_blob.resume.url
#   }
# }