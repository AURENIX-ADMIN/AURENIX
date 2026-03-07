resource "google_project" "client_project" {
  name       = "Aurenix ${var.client_slug} ${var.environment}"
  project_id = "aurenix-${var.client_slug}-${var.environment}"
  org_id     = var.org_id
  billing_account = var.billing_account_id
}

resource "google_project_service" "enabled_apis" {
  for_each = toset([
    "aiplatform.googleapis.com",
    "gmail.googleapis.com",
    "calendar.googleapis.com",
    "secretmanager.googleapis.com",
    "logging.googleapis.com"
  ])

  project = google_project.client_project.project_id
  service = each.key

  disable_on_destroy = false
}

resource "google_service_account" "agent_runtime" {
  account_id   = "sa-agent-runtime"
  display_name = "Agent Runtime Service Account"
  project      = google_project.client_project.project_id
}

resource "google_project_iam_member" "agent_vertex_user" {
  project = google_project.client_project.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_runtime.email}"
}

resource "google_project_iam_member" "agent_logging_writer" {
  project = google_project.client_project.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.agent_runtime.email}"
}
