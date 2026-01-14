locals {
  default = {
    split_tunnel = {
      mode = "exclude"
      addresses = [
        # Default
        "100.64.0.0/10",
        "169.254.0.0/16",
      ]
      hosts = [
        "batch.us-east-1.amazonaws.com", # Send batch jobs locally
        "fluidattacks.okta.com",         # Okta for proper authentication
      ]
    }
    device_settings_policy = {
      name       = "ZTNA"
      precedence = 10
      match = format(
        "any(identity.groups.name[*] in {\"%s\"}) or any(identity.groups.name[*] in {\"%s\"}) or any(identity.groups.name[*] in {\"%s\"})",
        local.okta.groups.continuous_analysts,
        local.okta.groups.dev,
        local.okta.groups.project_managers,
      )
      default = false
    }
    split_tunnel = {
      mode = "exclude"
      addresses = concat(
        local.default.split_tunnel.addresses,
        distinct(flatten([for _, tunnel in local.default : tunnel.routes])),
        [],
      )
    }
  }
}

resource "aws_s3_bucket" "s3_bucket" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_website_configuration" "s3_bucket" {
  bucket = aws_s3_bucket.s3_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_acl" "s3_bucket" {
  bucket = aws_s3_bucket.s3_bucket.id

  acl = "public-read"
}

resource "aws_s3_bucket_policy" "s3_bucket" {
  bucket = aws_s3_bucket.s3_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource = [
          aws_s3_bucket.s3_bucket.arn,
          "${aws_s3_bucket.s3_bucket.arn}/*",
        ]
      },
    ]
  })
}

resource "aws_s3_bucket_policy" "b" {
  bucket = aws_s3_bucket.b.id

  policy = <<POLICY
  {
    "Version": "2012-10-17",
    "Id": "MYBUCKETPOLICY",
    "Statement": [
      {
        "Sid": "IPAllow",
        "Effect": "Deny",
        "Principal": "*",
      }
    ]
  }
  POLICY
}

resource "null_resource" "add_prometheus" {
  triggers = {
    always_run = timestamp()
  }

  set {
    name  = "storageClass"
    value = "gp3"
  }

  depends_on = [
    null_resource.helm_add_prometheus
  ]
}

data "azurerm_key_vault_secret" "ms_user_db" {
  name         = "${var.keyvault.secret_abreviation}-ms-user-db"
  key_vault_id = data.azurerm_key_vault.this.id
}

variable "egress_rules" {
  type    = list(string)
  default = ["web", "app", "db"]
}

resource "aws_security_group" "safe_group" {
  name        = "safe_group"
  description = "Security Group for SFTP Server"
  vpc_id      = data.aws_vpc.selected.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = "127.0.0.1/32"
  }
  dynamic "egress" {
    for_each = var.egress_rules
    content {
      description = "my-test-group"
      from_port   = egress.value.from_port
      to_port     = egress.value.to_port
      protocol    = egress.value.protocol
      cidr_blocks = egress.value.cidr_blocks
    }
  }
}
