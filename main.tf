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

    azuread = {
      source               = "hashicorp/azuread"
      version              = "2.47.0"
    }

    acme = {
      source = "vancluever/acme"
      version = "2.21.0"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "cloudflare" {
  api_token                = var.CLOUDFLARE_API_TOKEN
}

provider "azuread" {
}

provider "acme" {
  server_url = "https://acme-v02.api.letsencrypt.org/directory"
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

    delivery_rule {
      name                 = "RedirectToHTTPS"
      order                = 1

      request_scheme_condition {
        operator           = "Equal"
        match_values       = ["HTTP"]
      }

      url_redirect_action {
        redirect_type      = "Found"
        protocol           = "Https"
      }
    }
}

data "azuread_client_config" "current" {}

resource "azuread_application" "letsencrypt" {
  display_name = "letsencrypt"
}

resource "azuread_service_principal" "letsencrypt" {
  client_id = azuread_application.letsencrypt.application_id
}

resource "time_rotating" "monthly" {
  rotation_days = 30
}

resource "azuread_service_principal_password" "letsencrypt" {
  service_principal_id = azuread_service_principal.letsencrypt.object_id
  rotate_when_changed = {
    rotation = time_rotating.monthly.id
  }
}

resource "tls_private_key" "private_key" {
  algorithm = "RSA"
}

resource "acme_registration" "me" {
  account_key_pem = tls_private_key.private_key.private_key_pem
  email_address   = var.EMAIL_ADDRESS
}

resource "azuread_service_principal" "cdn" {
  client_id           = "205478c0-bd83-4e1b-a9d6-db63a3e1e1c8"
}

resource "azurerm_key_vault" "resume" {
  name                     = "resume-key-vault"
  resource_group_name      = azurerm_resource_group.resume.name
  location                 = azurerm_resource_group.resume.location
  enabled_for_disk_encryption = true
  enabled_for_deployment   = true
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"

  access_policy {
    tenant_id              = data.azurerm_client_config.current.tenant_id
    object_id              = azuread_service_principal.cdn.object_id

    secret_permissions        = [
      "Get",
    ]

    certificate_permissions   = [
      "Get",
    ]
  }
    access_policy {
      tenant_id              = data.azurerm_client_config.current.tenant_id
      object_id              = data.azuread_client_config.current.object_id

      secret_permissions      = [
        "Get",
        "List",
        "Set",
        "Delete",
      ]

      certificate_permissions = [
        "Get",
        "List",
        "Set",
        "Delete",
        "Update",
        "Import",
        "Purge",
        "Recover",
        "Create",
      ]

      key_permissions         = [
        "Create",
        "Delete",
        "Get",
        "Import",
        "List",
        "Sign",
        "Update",
        "Verify",
        "Rotate",
      ]
    
    storage_permissions       = [
        "Get",
        "List",
        "Set",
        "Delete",
        "Update",
    ]
    }
  
}

resource "cloudflare_record" "resume" {
  zone_id                  = var.CLOUDFLARE_ZONE_ID
  name                     = var.DOMAIN_NAME
  value                    = azurerm_cdn_endpoint.resume.fqdn
  type                     = "CNAME"
  proxied                  = false
}

resource "acme_certificate" "resume" {
  account_key_pem          = acme_registration.me.account_key_pem
  email                    = var.EMAIL_ADDRESS
  common_name              = var.DOMAIN_NAME
  key_type                 = "2048"
  dns_challenge {
    provider               = "cloudflare"
    config = {
      CF_ZONE_API_TOKEN     = var.CLOUDFLARE_API_TOKEN
      CF_DNS_API_TOKEN     = var.CLOUDFLARE_API_TOKEN
      CLOUDFLARE_HTTP_TIMEOUT = "300"
    }
  }
}

resource "azurerm_key_vault_certificate" "resume" {
  name                     = replace(acme_certificate.resume.common_name, ".", "-")
  key_vault_id             = azurerm_key_vault.resume.id
  certificate {
    contents               = acme_certificate.resume.certificate_p12
  }
}

resource "azurerm_cdn_endpoint_custom_domain" "resume" {
  name                     = "resume-cdn-endpoint-custom-domain"
  cdn_endpoint_id          = azurerm_cdn_endpoint.resume.id
  host_name                = var.DOMAIN_NAME
    
    user_managed_https {
      key_vault_certificate_id = azurerm_key_vault_certificate.resume.id
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

resource "azurerm_storage_container" "functions" {
  name                     = "functions"
  storage_account_name     = azurerm_storage_account.resume.name
  container_access_type    = "private"
}

data "azurerm_storage_account_blob_container_sas" "functions" {
  connection_string        = azurerm_storage_account.resume.primary_connection_string
  container_name           = azurerm_storage_container.functions.name
  start                    = "2024-03-01T00:00:00Z"
  expiry                   = "2027-03-01T00:00:00Z"

  permissions {
    read                   = true
    write                  = false
    add                    = false
    create                 = false
    delete                 = false
    list                   = false
  }
}

variable "GIT_COMMIT_ID" {
  type = string
}

data "archive_file" "resume" {
  type        = "zip"
  source_dir  = "${path.module}/function"
  output_path = "${path.module}/function-app-${var.GIT_COMMIT_ID}.zip"
}

resource "azurerm_storage_blob" "functions" {
  name                     = "function-app-${var.GIT_COMMIT_ID}.zip"
  storage_account_name     = azurerm_storage_account.resume.name
  storage_container_name   = azurerm_storage_container.functions.name
  type                     = "Block"
  source                   = data.archive_file.resume.output_path
}

resource "azurerm_linux_function_app" "resume" {
  name                     = "jpolanskyresume-functionapp"
  location                 = azurerm_resource_group.resume.location
  resource_group_name      = azurerm_resource_group.resume.name
  service_plan_id          = azurerm_service_plan.resume.id
  storage_account_name     = azurerm_storage_account.resume.name
  storage_account_access_key = azurerm_storage_account.resume.primary_access_key
  https_only               = true
  builtin_logging_enabled  = false
  app_settings             = {
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "resumedb1_DOCUMENTDB" = azurerm_cosmosdb_account.resume.connection_strings[0]
    "SENDGRID_API_KEY"     = var.SENDGRID_API_KEY
    "WEBSITE_RUN_FROM_PACKAGE" = "https://${azurerm_storage_account.resume.name}.blob.core.windows.net/${azurerm_storage_container.functions.name}/${azurerm_storage_blob.functions.name}${data.azurerm_storage_account_blob_container_sas.functions.sas}"
  }

  site_config {
    application_insights_connection_string = azurerm_application_insights.resume.connection_string
    application_insights_key = azurerm_application_insights.resume.instrumentation_key

    application_stack {
      python_version       = "3.9"
    }

    cors {
      allowed_origins      = ["https://${var.DOMAIN_NAME}"]
    }
  }
}