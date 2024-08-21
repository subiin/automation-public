/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

locals {
  projects = (
    var.quota_config.projects == null
    ? [var.project_id]
    : var.quota_config.projects
  )
}

module "project" {
  source         = "../../../modules/project"
  name           = var.project_id
  project_create = var.project_create
  services = [
    "compute.googleapis.com",
    "cloudfunctions.googleapis.com"
  ]
  iam = {
    "roles/monitoring.metricWriter" = [module.cf.service_account_iam_email]
  }
}

module "pubsub" {
  source     = "../../../modules/pubsub"
  project_id = module.project.project_id
  name       = var.name
  subscriptions = {
    "${var.name}-default" = null
  }
  # the Cloud Scheduler robot service account already has pubsub.topics.publish
  # at the project level via roles/cloudscheduler.serviceAgent
}

module "cf" {
  source      = "../../../modules/cloud-function"
  project_id  = module.project.project_id
  name        = var.name
  region      = var.region
  bucket_name = "${var.name}-${random_pet.random.id}"
  bucket_config = {
    location = var.region
  }
  bundle_config = {
    source_dir  = "cf"
    output_path = var.bundle_path
  }
  # https://github.com/hashicorp/terraform-provider-archive/issues/40
  # https://issuetracker.google.com/issues/155215191
  environment_variables = {
    USE_WORKER_V2                         = "true"
    PYTHON37_DRAIN_LOGS_ON_CRASH_WAIT_SEC = "5"
  }
  service_account_create = true
  trigger_config = {
    v1 = {
      event    = "google.pubsub.topic.publish"
      resource = module.pubsub.topic.id
    }
  }
}

resource "google_cloud_scheduler_job" "job" {
  project   = var.project_id
  region    = var.region
  name      = var.name
  schedule  = var.schedule_config
  time_zone = "UTC"

  pubsub_target {
    attributes = {}
    topic_name = module.pubsub.topic.id
    data = base64encode(jsonencode({
      gce_project = var.quota_config.projects
      gce_region  = var.quota_config.regions
      keywords    = var.quota_config.filters
    }))
  }
}

resource "google_project_iam_member" "network_viewer" {
  for_each = toset(local.projects)
  project  = each.key
  role     = "roles/compute.networkViewer"
  member   = module.cf.service_account_iam_email
}

resource "google_project_iam_member" "quota_viewer" {
  for_each = toset(local.projects)
  project  = each.key
  role     = "roles/servicemanagement.quotaViewer"
  member   = module.cf.service_account_iam_email
}


resource "google_monitoring_alert_policy" "alert_policy" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - CPU Count"
  combiner     = "OR"
  conditions {
    display_name = "simple quota threshold for cpus count"
    condition_threshold {
      # filter          = "metric.type=\"custom.googleapis.com/quota/cpus_utilization\" resource.type=\"global\""
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/allocation/usage\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"compute.googleapis.com/cpus\""
      threshold_value = 10
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "GCE cpus quota over threshold."
  }
}

resource "google_monitoring_alert_policy" "alert_policy2" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - BigQuery Total Slots"
  combiner     = "OR"
  conditions {
    display_name = "simple quota threshold for BigQuery slots"
    condition_threshold {
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/allocation/usage\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"bigqueryreservation.googleapis.com/total_slots\""
      threshold_value = 50
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "BigQuery slots quota over threshold."
  }
}

resource "google_monitoring_alert_policy" "alert_policy3" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - BigQuery Usage"
  combiner     = "OR"
  conditions {
    display_name = "simple limit threshold for BigQuery usage"
    condition_threshold {
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/exceeded\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"bigquery.googleapis.com/quota/query/usage\""
      threshold_value = 0
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_COUNT_TRUE"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "BigQuery Usage limit over threshold."
  }
}

resource "google_monitoring_alert_policy" "alert_policy4" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - Service Account Count"
  combiner     = "OR"
  conditions {
    display_name = "simple quota threshold for SA count"
    condition_threshold {
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/allocation/usage\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"iam.googleapis.com/quota/service-account-count\""
      threshold_value = 10
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "Service Account Count quota over threshold."
  }
}

resource "google_monitoring_alert_policy" "alert_policy5" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - Compute Engine Instances"
  combiner     = "OR"
  conditions {
    display_name = "simple quota threshold for Compute Engine Instances"
    condition_threshold {
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/allocation/usage\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"compute.googleapis.com/instances\""
      threshold_value = 10
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "Compute Engine Instances quota over threshold."
  }
}

resource "google_monitoring_alert_policy" "alert_policy6" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - In Use Adresses(Global)"
  combiner     = "OR"
  conditions {
    display_name = "simple quota threshold for global_in_use_addresses"
    condition_threshold {
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/allocation/usage\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"compute.googleapis.com/compute.googleapis.com/global_in_use_addresses\""
      threshold_value = 10
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "Global_in_use_addresses quota over threshold."
  }
}

resource "google_monitoring_alert_policy" "alert_policy7" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - In Use Adresses(Regional)"
  combiner     = "OR"
  conditions {
    display_name = "simple quota threshold for regional_in_use_addresses"
    condition_threshold {
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/allocation/usage\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"compute.googleapis.com/regional_in_use_addresses\""
      threshold_value = 10
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "Regional_in_use_addresses quota over threshold."
  }
}

resource "google_monitoring_alert_policy" "alert_policy8" {
  count        = var.alert_create ? 1 : 0
  project      = module.project.project_id
  display_name = "Quota monitor - Firewalls"
  combiner     = "OR"
  conditions {
    display_name = "simple quota threshold for Firewall count"
    condition_threshold {
      filter          = "metric.type=\"serviceruntime.googleapis.com/quota/allocation/usage\" resource.type=\"consumer_quota\" metric.label.quota_metric=\"compute.googleapis.com/firewalls\""
      threshold_value = 10
      comparison      = "COMPARISON_GT"
      duration        = "0s"
      aggregations {
        alignment_period   = "60s"
        group_by_fields    = []
        per_series_aligner = "ALIGN_MEAN"
      }
      trigger {
        count   = 1
        percent = 0
      }
    }
  }
  enabled = false
  user_labels = {
    name = var.name
  }
  documentation {
    content = "Firewall count quota over threshold."
  }
}

resource "random_pet" "random" {
  length = 1
}
