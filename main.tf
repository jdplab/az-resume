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

resource "azurerm_cdn_frontdoor_profile" "resume" {
  name                = "resume-cdn"
  resource_group_name = azurerm_resource_group.resume.name
  sku_name            = "Standard_AzureFrontDoor"
}

resource "azurerm_cdn_endpoint" "resume" {
  name                = "resume-cdn-endpoint"
  profile_name        = azurerm_cdn_frontdoor_profile.resume.name
  resource_group_name = azurerm_resource_group.resume.name
  location            = azurerm_resource_group.resume.location
  origin_host_header  = azurerm_storage_account.resume.primary_web_endpoint
    origin {
      name            = "resume-origin"
      host_name       = azurerm_storage_account.resume.primary_web_endpoint
    }
}