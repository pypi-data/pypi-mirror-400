import os

#PATH
DEST_PATH = os.path.join(os.getcwd(), "output", "pdf")

#Constant N8N
N8N_AUTH = (os.getenv("N8N_USERNAME"), os.getenv("N8N_PASSWORD"))
API_DOMAIN_N8N_URL = os.getenv("DOMAIN_URL")
FORNECEDOR_N8N_DOMAIN = "fornecedor"
CENTRO_N8N_DOMAIN = "centro"

# Constantes dos ID's de Formulario
FORM_TEMPLATE_AUTOMACAO   = "910a886b-701a-490d-8b02-708b6c2d9881"
FORM_TEMPLATE_COMPLEMENTO = "720b4c69-9d84-4f08-930e-1d6c22805f71"
FORM_TEMPLATE_SERVICO     = "6545f970-bc4f-413c-9a77-de3611a3a615"

# Constants das Issue Jira
ISSUE_TYPE_CONSUMO = "Aprovações NFs - Consumo"
ISSUE_TYPE_SERVICO = "Aprovações NFs - Serviço"
ISSUE_CUSTOMFIELD_NF_DOCUMENT_ID = 'customfield_11115'
TIPO_DE_ALOCACAO_DE_DESPESA_RATEIO = '3'
RATEIO_FORM_SUMITTED = 's'
SEM_RETENCAO = 'Sem retenção'

# SAP Constants
SAP_NOTA_FISCAL = "ME21N"
SAP_FATURA = "FV60"
ZCOR = 'ZCOR'
ZAIM = 'ZAIM'

# Constants Jira
JIRA_AUTH = (os.getenv("USER"), os.getenv("ACCESS_TOKEN"))
API_ISSUE_URL = os.getenv("ISSUE_URL")
API_FORM_URL = os.getenv("FORM_URL")
CLOUD_ID = os.getenv("CLOUD_ID")



API_HEADERS = {
                "Accept": "application/json",
                "Content-Type": "application/json",
              }

API_ATTACHMENT_HEADERS = {
                            "Accept": "*/*",
                         }

API_ATLASSIAN_HEADERS = {
                            "Accept": "application/json",
                            "X-ExperimentalApi": "opt-in",
                        }

# Reference From Miro
SERIE_NF = '001'
MAX_LEN_NRO_NF = 6
CONDICOES_PAGAMENTO_30DIAS = '0000'
#Test Constants
ISSUE_KEY = "GHN-643"
TRASITION_PEDIDO_CRIADO = '241'
TRASITION_REVISAR_ERRO  = '231'
FORM_COMPLEMENTO_ID = "f1671ecd-fc44-418f-b6e3-88d774a4b0d4"
FORM_AUTOMACAO_ID = "e6214bb3-eafc-4de8-ad5a-c8b387346c3e"
STATUS_LIBERADO = "2"
STATUS_BLOQUEADO = "1"
# Jira Form Nota de Pedido
VALOR_LIQUIDO_DA_FATURA = "valor_liquido"
JUROS_DA_FATURA = "juro"
CEM_PORCENTO_DO_VALOR_BRUTO = 100.00
# # Constantes do Anexo Json
ID_DO_LOCATARIO = "TenantId"
NOME_DA_INTEGRACAO = "IntegrationName"
NOME_DO_USUARIO = "UserName"
EMAIL_DO_USUARIO = "UserEmail"
ID_DA_FATURA = "InvoiceId"
NUMERO_DA_FATURA_DO_APLICATIVO = "AplicationInvoiceNumber"
CNPJ_DO_FORNECEDOR = "SupplierCnpj"
RAZAO_SOCIAL_DO_FORNECEDOR = "SupplierCorporateName"
CNPJ_DO_CLIENTE = "ClientCnpj"
RAZAO_SOCIAL_DO_CLIENTE = "ClientCorporateName"
ENDERECO_DO_FORNECEDOR = "SupplierAddress"
ENDERECO_DO_CLIENTE = "ClientAddress"
DATA_DE_VENCIMENTO = "DueDate"
DATA_DE_EMISSAO = "DateOfIssue"
DATA_DE_REFERENCIA = "ReferenceDate"
DATA_DE_REGISTRO = "DateRegister"
VALOR_TOTAL_DA_FATURA = "TotalInvoiceAmount"
VALOR_BRUTO_DA_FATURA = "GrossInvoiceValue"
CODIGO_DE_BARRAS = "BarCode"
NUMERO_DA_FATURA = "InvoiceNumber"
NUMERO_DE_SERVICO = "nro_servico"
NUMERO_FISCAL = "nro_fiscal"
UNIDADE_LOJA = "unidade_loja"
CODIGO_IMPOSTO = "cod_imp"
CODIGO_FORNECEDOR = "sap_cod_fornecedor"
CODIGO_DE_SERVICO = "cod_servico"
CODIGO_SAP_SERVICO = "sap_cod_servico"
CHAVE_DE_ACESSO_DA_FATURA = "InvoiceAccessKey"
NUMERO_DA_FATURA_DO_FORNECEDOR = "SupplierInvoiceNumber"
CODIGO_DE_DEBITO_AUTOMATICO = "AutomaticDebitCode"
INFORMACAO_DA_FATURA = "InvoiceInformation"
OBSERVACAO_DA_FATURA = "InvoiceObservation"
NOME_DO_FORNECEDOR = "SupplierName"
NUMERO_DO_CONTRATO = "ContractNumber"
ID_DO_CONTRATO = "ContractId"
STATUS_DO_CONTRATO = "ContractStatus"
STATUS_DA_FATURA = "InvoiceStatus"
LOCALIZACAO_DO_CONTRATO = "ContractLocation"
VERTICAL_DO_FORNECEDOR = "SupplierVertical"
PROTOCOLO_DE_LANCAMENTO = "launchProtocol"
SERVICOS_DA_FATURA = "InvoiceServices"
IMPOSTOS = "Taxes"
CAMPOS_CUSTOMIZADOS = "CustomFields"
ALOCACOES_DE_CUSTO = "CostAllocations"
ARQUIVOS_DA_FATURA = "InvoiceFiles"
COMPLEMENTO_DE_AGUA = "WaterComplement"
COMPLEMENTO_DE_ENERGIA = "EnergyComplement"
COMPLEMENTO_DE_GAS = "GasComplement"
POSSUI_CHAVE_ACESSO = "possui_chave_acesso"
ORDEM_INTERNA = 'ord_interna'
TEXTO_BREVE = "texto_breve"
CODIGO_VERIFICACAO = "cod_verificacao"
CENTRO_DE_CUSTO = "centro_custo"
CONTA_RAZAO = "conta_razao"
PROTOCOLO_AUTORIZACAO = "numero_log"
DATA_AUTORIZACAO = "data_procmto"
HORA_AUTORIZACAO = "hora_procmto"
GRUPO_COMPRADORES = "grupo_compradores"
ORG_COMPRAS = "org_compras"
IMPOSTO_SEM_RETENCAO = "imposto_sem_retencao"
#Constantes de Validação
OPTIONAL_FIELDS_CONSUMO = [
    "nro_fatura",
    "nro_nota_fiscal",
    "valor_liquido",
    "juros",
    "data_leitura_atual",
    "data_leitura_anterior"
]

OPTIONAL_FIELDS_SERVICO = [
    "nro_fatura",
    "nro_nota_fiscal",
    "valor_liquido",
    "juros",
    "data_leitura_atual",
    "data_leitura_anterior"
]

SEFAZ_FIELDS = [
    "data_autorizacao",
    "hora_autorizacao",
    "protocolo_autorizacao",
    "chave_acesso"
]

FISCAL_FIELDS = [
    "InvoiceNumber"
]

FATURA_FIELDS = [
    "SupplierInvoiceNumber"
]
NRO_DOCUMENTO_PEDIDO_FIELD = 'customfield_11147'

AUTOMACAO_FORM_TEMPLATE_ID= '910a886b-701a-490d-8b02-708b6c2d9881'
NF_CAIXA_FORM_TEMPLATE_ID = '3fdd462b-a53e-4119-b44b-1adc5c7c96d1'
NRO_DOCUMENTO_NOTA_FISCAL = 'nro_documento_nota_fiscal'
MODALID_FRET_9 = '9'