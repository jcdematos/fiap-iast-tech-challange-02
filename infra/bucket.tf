resource "aws_s3_bucket" "medallion-bucket" {
  bucket = "fiap-datalake-tech"

  tags = {
    Name        = "fiap-datalake-tech"
    Environment = "Dev"
  }
}

resource "aws_s3_object" "layers" {
  for_each = toset(local.layers)
  bucket       = aws_s3_bucket.medallion-bucket.id
  key          = each.value
  content_type = "application/x-directory"
}

