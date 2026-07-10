output "api_gateway_endpoint_ref" { value = "resource-manager-output:api_gateway_endpoint" }
output "oracle_26ai_connect_descriptor_secret_ref" { value = "oci-vault-managed:oracle-26ai-connect-descriptor" }
output "valkey_endpoint_secret_ref" { value = "oci-vault-managed:redis-endpoint" }
output "oci_genai_endpoint_ref" { value = "resource-manager-output:oci-genai-endpoint" }
output "ocir_repository_refs" { value = ["resource-manager-output:ocir-control-plane-api"] }
