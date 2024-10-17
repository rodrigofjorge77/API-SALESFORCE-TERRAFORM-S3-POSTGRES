provider "aws" {
  region = "us-east-2"  # Altere para a região que você preferir
}

# Bucket creation
resource "aws_s3_bucket" "my_s3_bucket"{
    bucket = "rodrigojorge-projeto202410-salesforce"

    tags = {
    Name = "My bucket"
    Enviroment ="Dev"
  }
}

# Criando um Security Group para o RDS
resource "aws_security_group" "rds_sg" {
  name        = "allow_postgres"
  description = "Allow PostgreSQL inbound traffic"
  vpc_id      = "vpc-0665be019aa8c60dd"  # Insira o ID da VPC correta

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Permitir tráfego de qualquer IP, mas idealmente, restrinja isso
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds_security_group"
  }
}

# Criando a instância do PostgreSQL RDS
resource "aws_db_instance" "postgres_instance" {
  allocated_storage    = 20                      # Usando o limite da camada gratuita
  max_allocated_storage = 100                    # Define até onde o armazenamento pode aumentar (pague conforme usar)
  engine               = "postgres"
  #engine_version       = "16.3-R2"               # Versão do PostgreSQL
  instance_class       = "db.t4g.micro"           # Instância dentro da camada gratuita
  username             = "salesforce"                 # Altere para seu nome de usuário
  password             = "salesforce"                 # Coloque uma senha segura
  #parameter_group_name = "default.postgres13"
  skip_final_snapshot  = true                    # Não cria snapshot final ao destruir
  publicly_accessible  = true                    # Permite acesso público (verificar se é necessário)
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  tags = {
    Name = "meu-postgres-db"
  }
}

# Outputs para facilitar a visualização das informações
output "bucket_name" {
  value = aws_s3_bucket.my_s3_bucket.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.postgres_instance.endpoint
}

output "rds_username" {
  value = aws_db_instance.postgres_instance.username
}

