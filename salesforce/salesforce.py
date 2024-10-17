import requests
import ast
import json
import pandas as pd
import io
from minio import Minio
from minio.error import S3Error
import pandas as pd
from sqlalchemy import create_engine

# Conectar ao S3 com Minio (usando credenciais da AWS)
client = Minio(
    "s3.amazonaws.com",  # URL do endpoint S3
    access_key="",
    secret_key="",
    secure=True  # Conexão segura HTTPS
)

def upload_arquivo_s3(arquivo_local, nome_bucket, caminho_s3):
    try:
        # Fazer upload do arquivo
        client.fput_object(nome_bucket, caminho_s3, arquivo_local)
        print(f'Upload de {arquivo_local} para s3://{nome_bucket}/{caminho_s3} concluído com sucesso!')
    except S3Error as err:
        print(f"Ocorreu um erro: {err}")

url = "https://login.salesforce.com/services/oauth2/token?username=rodrigofjorge@gmail.com&password=Kimera36917tuCTf3bMFoBrugCPHA5bylj&grant_type=password&client_id=3MVG9JJwBBbcN47KnzfNaTKVsybjsxDQRIs5bydZzBywsQgXM40xoutiG117L469Q7YX2FGtSV5Nr6txEtRmQ&client_secret=F71EA9A9A538A8A9221B864CBB43D53C0E6C881286BCEB9B5C319DA0F5FD2B59"

payload = {'grant_type': 'password',
'client_id': '',
'client_secret': '',
'username': '',
'password': ''}        

files=[]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

dicResponse = ast.literal_eval(response.text)

token = dicResponse.get("access_token")

url = "salesforce.com/services/data/v50.0/jobs/query"

payload = json.dumps({
  "operation": "query",
  "query": "SELECT Id, FirstName, LastName, Email, Phone, AccountId, MailingStreet, MailingCity, MailingState, MailingPostalCode, MailingCountry, CreatedDate, LastModifiedDate FROM Contact",
  "contentType": "CSV",
  "columnDelimiter": "SEMICOLON",
  "lineEnding": "CRLF"
})

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
  'Cookie': 'BrowserId=1K1o8PtKEe63M4lWtso1qw; CookieConsentPolicy=0:1; LSKey-c$CookieConsentPolicy=0:1'
}

response = requests.request("POST", url, headers=headers, data=payload)

dicResponse = ast.literal_eval(response.text)
id = dicResponse.get("id")

url = "salesforce.com/services/data/v50.0/jobs/query/" + id + "/results"

payload = {}
headers = {
  'Accept': 'text/csv',
  'Authorization': 'Bearer ' + token,
  'Cookie': 'BrowserId=1K1o8PtKEe63M4lWtso1qw; CookieConsentPolicy=0:1; LSKey-c$CookieConsentPolicy=0:1'
}

response = requests.request("GET", url, headers=headers, data=payload)

csv_file = io.StringIO(response.text)

# Abrindo um arquivo CSV para escrita
with open('saida.csv', 'w') as arquivo_csv:
    # Gravando o conteúdo do StringIO no arquivo CSV
    arquivo_csv.write(csv_file.getvalue())

print("Arquivo CSV exportado com sucesso!")

# Carregar o conteúdo da string no DataFrame
df = pd.read_csv(csv_file, sep=';', quotechar='"')

# Variáveis de exemplo
arquivo_local = 'saida.csv'  # Caminho do arquivo local
nome_bucket = 'projeto202410-salesforce'  # Nome do bucket S3
caminho_s3 = 'files/saida.csv'  # Caminho do arquivo no bucket

# Chamar a função para fazer o upload
upload_arquivo_s3(arquivo_local, nome_bucket, caminho_s3)

# Criar uma conexão com o banco de dados PostgreSQL
usuario = 'salesforce'
senha = 'salesforce'
host = 'us-east-2.rds.amazonaws.com'  # ou o IP do seu servidor
porta = '5432'  # Porta padrão do PostgreSQL
banco_dados = 'postgres'

# String de conexão
engine = create_engine(f'postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco_dados}')

# Nome da tabela no banco de dados
nome_tabela = 'contato'

# Inserir ou atualizar os dados na tabela
# O parâmetro 'if_exists' pode ser 'replace', 'append' ou 'fail'
df.to_sql(nome_tabela, engine, if_exists='replace', index=False)

print("Dados inseridos ou atualizados na tabela com sucesso!")