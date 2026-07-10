terraform {
  required_version = ">= 1.6.0"
  required_providers {
    oci = { source = "oracle/oci", version = ">= 6.0.0" }
  }
}

module "network" { source = "./modules/network" }
module "iam" { source = "./modules/iam" }
module "api_gateway" { source = "./modules/api-gateway" }
module "oke" { source = "./modules/oke" }
module "functions" { source = "./modules/functions" }
module "oracle_26ai" { source = "./modules/oracle-26ai" }
module "cache_valkey" { source = "./modules/cache-valkey" }
module "genai" { source = "./modules/genai" }
module "devops" { source = "./modules/devops" }
module "ocir" { source = "./modules/ocir" }
module "vault" { source = "./modules/vault" }
module "observability" { source = "./modules/observability" }
