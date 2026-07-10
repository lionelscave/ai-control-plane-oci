variable "compartment_ocid" { type = string }
variable "region" { type = string }
variable "environment" { type = string default = "dev" }
variable "approval_required" { type = bool default = true }
