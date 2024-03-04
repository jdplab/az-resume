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
  api_token                = var.CLOUDFLARE_API_TOKEN
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
  value                    = azurerm_cdn_endpoint.resume.fqdn
  type                     = "CNAME"
  proxied                  = false
}

resource "cloudflare_record" "cdnverify" {
  zone_id                  = var.CLOUDFLARE_ZONE_ID
  name                     = "cdnverify.${var.DOMAIN_NAME}"
  value                    = "cdnverify.${azurerm_cdn_endpoint.resume.fqdn}"
  type                     = "CNAME"
  proxied                  = false
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

resource "azurerm_cosmosdb_account" "resume" {
  name                     = var.COSMOSDB_ACCOUNT_NAME
  resource_group_name      = azurerm_resource_group.resume.name
  location                 = azurerm_resource_group.resume.location
  offer_type               = "Standard"
  enable_free_tier         = true

  geo_location {
    location               = "eastus"
    failover_priority      = 0
  }
  
  consistency_policy {
    consistency_level      = "Session"
  }
}

resource "azurerm_cosmosdb_sql_database" "resume" {
  name                     = "resumedb"
  resource_group_name      = azurerm_resource_group.resume.name
  account_name             = azurerm_cosmosdb_account.resume.name
}

resource "azurerm_cosmosdb_sql_container" "resume" {
  name                     = "resumecontainer"
  resource_group_name      = azurerm_resource_group.resume.name
  account_name             = azurerm_cosmosdb_account.resume.name
  database_name            = azurerm_cosmosdb_sql_database.resume.name
  partition_key_path       = "/id"
  throughput               = 400
}

resource "azurerm_application_insights" "resume" {
  name                     = "resumeappinsights"
  location                 = azurerm_resource_group.resume.location
  resource_group_name      = azurerm_resource_group.resume.name
  application_type         = "web"
  }

resource "azurerm_service_plan" "resume" {
  name                     = "resumeappserviceplan"
  location                 = azurerm_resource_group.resume.location
  resource_group_name      = azurerm_resource_group.resume.name
  os_type                  = "Linux"
  sku_name                 = "Y1"
}

resource "azurerm_linux_function_app" "resume" {
  name                     = "jpolanskyresume-functionapp"
  location                 = azurerm_resource_group.resume.location
  resource_group_name      = azurerm_resource_group.resume.name
  service_plan_id          = azurerm_service_plan.resume.id
  storage_account_name     = azurerm_storage_account.resume.name
  storage_account_access_key = azurerm_storage_account.resume.primary_access_key
  https_only               = true
  app_settings             = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "resumedb1_resumedb" = "AccountEndpoint=${azurerm_cosmosdb_account.resume.endpoint};AccountKey=${azurerm_cosmosdb_account.resume.primary_key};"
  }

  site_config {
    application_insights_connection_string = azurerm_application_insights.resume.connection_string
    application_insights_key = azurerm_application_insights.resume.instrumentation_key

    application_stack {
      python_version       = "3.9"
    }
  }
}