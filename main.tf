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

  blob_properties {
    cors_rule {
      allowed_headers      = ["*"]
      allowed_methods      = ["GET"]
      allowed_origins      = ["https://jon-polansky.com"]
      exposed_headers      = ["*"]
      max_age_in_seconds   = 3600
    }
  }
}

resource "azurerm_storage_container" "admin" {
  name                     = "admin"
  storage_account_name     = azurerm_storage_account.resume.name
  container_access_type    = "private"
}

resource "azurerm_storage_container" "blogposts" {
  name                     = "blogposts"
  storage_account_name     = azurerm_storage_account.resume.name
  container_access_type    = "private"
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

    delivery_rule {
      name                 = "CallbackRedirect"
      order                = 2

      url_path_condition {
        operator           = "EndsWith"
        match_values       = ["/.auth/login/aadb2c/callback"]
      }

      url_redirect_action {
        redirect_type      = "Found"
        protocol           = "Https"
        hostname           = var.DOMAIN_NAME
        path               = "/callback.html"
      }
    }
}

data "azurerm_aadb2c_directory" "resume" {
  resource_group_name      = azurerm_resource_group.resume.name
  domain_name              = "azresume.onmicrosoft.com"
}

data "azuread_client_config" "current" {}

resource "azuread_application" "letsencrypt" {
  display_name = "letsencrypt"
}

resource "azuread_service_principal" "letsencrypt" {
  client_id = azuread_application.letsencrypt.client_id
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

data "azuread_service_principal" "cdn" {
  client_id           = "205478c0-bd83-4e1b-a9d6-db63a3e1e1c8"
}

resource "azurerm_key_vault" "resume" {
  name                     = "resume-key-vault"
  resource_group_name      = azurerm_resource_group.resume.name
  location                 = azurerm_resource_group.resume.location
  enabled_for_disk_encryption = true
  enabled_for_deployment   = true
  tenant_id                = data.azuread_client_config.current.tenant_id
  sku_name                 = "standard"

  access_policy {
    tenant_id              = data.azuread_client_config.current.tenant_id
    object_id              = data.azuread_service_principal.cdn.object_id

    secret_permissions        = [
      "Get",
      "List",
      "Set",
      "Delete",
    ]

    certificate_permissions   = [
      "Get",
      "List",
      "Delete",
      "Update",
      "Import",
      "Purge",
      "Recover",
      "Create",
    ]
  }
    access_policy {
      tenant_id              = data.azuread_client_config.current.tenant_id
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

resource "cloudflare_record" "cdnverify" {
  zone_id                  = var.CLOUDFLARE_ZONE_ID
  name                     = "cdnverify.${var.DOMAIN_NAME}"
  value                    = "cdnverify.${azurerm_cdn_endpoint.resume.fqdn}"
  type                     = "CNAME"
  proxied                  = false
}

resource "acme_certificate" "resume" {
  account_key_pem          = acme_registration.me.account_key_pem
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
      key_vault_secret_id = azurerm_key_vault_certificate.resume.secret_id
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
  name                     = "visitorcount"
  resource_group_name      = azurerm_resource_group.resume.name
  account_name             = azurerm_cosmosdb_account.resume.name
  database_name            = azurerm_cosmosdb_sql_database.resume.name
  partition_key_path       = "/id"
  throughput               = 400
}

resource "azurerm_cosmosdb_sql_container" "blogposts" {
  name                     = "blogposts"
  resource_group_name      = azurerm_resource_group.resume.name
  account_name             = azurerm_cosmosdb_account.resume.name
  database_name            = azurerm_cosmosdb_sql_database.resume.name
  partition_key_path       = "/id"
  throughput               = 400
}

resource "azurerm_cosmosdb_sql_container" "comments" {
  name                     = "comments"
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

data "azurerm_subscription" "current" {
}

data "azuread_service_principal" "current" {
  display_name = "terraform"
}

resource "time_rotating" "semi-annually" {
  rotation_days = 180
}

resource "azuread_service_principal_password" "current" {
  service_principal_id = data.azuread_service_principal.current.object_id
  rotate_when_changed = {
    rotation = time_rotating.semi-annually.id
  }
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
    "STORAGE_CONNECTIONSTRING" = azurerm_storage_account.resume.primary_connection_string
    "BLOGPOSTS_CONTAINER"  = azurerm_storage_container.blogposts.name
    "WEB_CONTAINER"        = "$web"
    "SUBSCRIPTION_ID"      = data.azurerm_subscription.current.subscription_id
    "RESOURCE_GROUP_NAME"  = azurerm_resource_group.resume.name
    "PROFILE_NAME"         = azurerm_cdn_profile.resume.name
    "ENDPOINT_NAME"        = azurerm_cdn_endpoint.resume.name
    "AZURE_CLIENT_ID"      = data.azuread_service_principal.current.client_id
    "AZURE_TENANT_ID"      = data.azuread_client_config.current.tenant_id
    "AZURE_CLIENT_SECRET"  = azuread_service_principal_password.current.value
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