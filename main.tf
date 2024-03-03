terraform {

  backend "remote" {
    organization           = "JP-Lab"

    workspaces {
      name                 = "azure-resume"
    }
  }
}

terraform {
  required_providers {
    azurerm = {
      source               = "hashicorp/azurerm"
      version              = "3.94.0"
    }

    cloudflare = {
      source               = "cloudflare/cloudflare"
      version              = "4.25.0"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "cloudflare" {
  api_token                = VAR.CLOUDFLARE_API_TOKEN
}

resource "azurerm_resource_group" "resume" {
  name                     = var.RESOURCE_GROUP_NAME
  location                 = var.LOCATION
}

resource "azurerm_storage_account" "resume" {
  name                     = var.STORAGE_ACCOUNT_NAME
  resource_group_name      = azurerm_resource_group.resume.name
  location                 = azurerm_resource_group.resume.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  static_website {
    index_document         = "index.html"
  }
}

resource "azurerm_cdn_profile" "resume" {
  name                     = "resume-cdn-profile"
  resource_group_name      = azurerm_resource_group.resume.name
  location                 = azurerm_resource_group.resume.location
  sku                      = "Standard_Microsoft"
}

resource "azurerm_cdn_endpoint" "resume" {
  name                     = "resume-cdn-endpoint"
  profile_name             = azurerm_cdn_profile.resume.name
  resource_group_name      = azurerm_resource_group.resume.name
  location                 = azurerm_resource_group.resume.location
  origin_host_header       = azurerm_storage_account.resume.primary_web_host
    origin {
      name                 = "resume-origin"
      host_name            = azurerm_storage_account.resume.primary_web_host
    }
}

resource "cloudflare_record" "resume" {
  zone_id                  = var.CLOUDFLARE_ZONE_ID
  name                     = var.DOMAIN_NAME
  value                    = azurerm_cdn_endpoint.resume.host_name
  type                     = "CNAME"
  proxied                  = true
}

resource "azurerm_cdn_endpoint_custom_domain" "resume" {
  name                     = "resume-cdn-endpoint-custom-domain"
  cdn_endpoint_id          = azurerm_cdn_endpoint.resume.id
  host_name                = var.DOMAIN_NAME
    cdn_managed_https {
      certificate_type     = "Dedicated"
      protocol_type        = "ServerNameIndication"
    }
}