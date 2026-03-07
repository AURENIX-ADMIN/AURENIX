module "client_seed" {
  source = "./modules/client-factory"

  client_id   = "seed"
  client_slug = "aurenix-seed"
  environment = "dev"
  
  billing_account_id = var.billing_account_id
  org_id             = var.org_id
}
