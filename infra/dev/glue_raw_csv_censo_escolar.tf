locals {
  censo_escolar_years = toset([
    "2023",
    "2024",
  ])
}

resource "aws_s3_object" "raw_csv_censo_escolar_script" {
  bucket = aws_s3_bucket.glue_scripts.id
  key    = "jobs/bronze/raw_csv_censo_escolar.py"
  source = "../../glue/bronze/raw_csv_censo_escolar.py"
  etag   = filemd5("../../glue/bronze/raw_csv_censo_escolar.py")
}

resource "aws_glue_job" "raw_csv_censo_escolar" {
  for_each = local.censo_escolar_years

  name              = "raw-csv-bronze-censo-escolar-${each.key}"
  description       = "Reads Censo Escolar microdados_ed_basica CSV for ${each.key} from S3 raw layer into S3 bronze layer"
  role_arn          = "arn:aws:iam::161582022021:role/glue-role"
  glue_version      = "5.0"
  max_retries       = 0
  timeout           = 60
  number_of_workers = 2
  worker_type       = "G.1X"
  execution_class   = "STANDARD"

  command {
    script_location = "s3://${aws_s3_bucket.glue_scripts.bucket}/jobs/bronze/raw_csv_censo_escolar.py"
    name            = "glueetl"
    python_version  = "3"
  }

  notification_property {
    notify_delay_after = 3
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--continuous-log-logGroup"          = "/aws-glue/jobs"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-continuous-log-filter"     = "true"
    "--enable-metrics"                   = ""
    "--year"                             = each.key
  }

  execution_property {
    max_concurrent_runs = 1
  }

  tags = {
    "ManagedBy" = "Terraform"
    "Dataset"   = "censo_escolar"
  }
}
