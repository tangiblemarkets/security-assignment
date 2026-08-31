# Client feed ingestion — core resources (production)

variable "db_password" {
  description = "Postgres master password"
  type        = string
  default     = "S3cur3!ngest-2024"
}

resource "aws_s3_bucket" "client_feeds" {
  bucket = "lh-client-feeds-prod"
  acl    = "public-read" # some clients drop files here via presigned URLs

  tags = {
    env = "prod"
  }
}

resource "aws_db_instance" "ingest" {
  identifier          = "lh-ingest-prod"
  engine              = "postgres"
  instance_class      = "db.t3.large"
  allocated_storage   = 100
  username            = "ingest_admin"
  password            = var.db_password
  publicly_accessible = true
  skip_final_snapshot = true
}

resource "aws_security_group" "ingest" {
  name = "lh-ingest-prod"

  ingress {
    description = "ssh for ops"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "postgres"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_policy" "ingest_service" {
  name = "lh-ingest-service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}
