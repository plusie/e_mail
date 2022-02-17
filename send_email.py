#!pip install emoji

import emoji
import logging
import pandas
import smtplib
import ssl
from email.message import EmailMessage

# DADOS DO E-MAIL DE ORIGEM
FROM = {
    'e_mail': "abc@servidor.com.br",
    'PWD': "12345", # Caso use verificação em 2 etapas, clicar em config > Seguranca > Criar senha app  
    'SMTP_SERVER': "smtp.gmail.com",
    'PORT': 587  
} 

# Logando
logger = logging.getLogger(__name__)

log_console = logging.StreamHandler()
log_console.setLevel(logging.WARNING)
log_console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
log_console.setFormatter(log_console_format)
logger.addHandler(log_console)

log_file = logging.FileHandler('send_email.log')
log_file.setLevel(logging.DEBUG)
log_file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_file.setFormatter(log_file_format)
logger.addHandler(log_file)

# Carregando arquivo CSV com dados a serem enviados incluindo o e-mail de destino
df = pandas.read_csv('voucher.csv', 
            #index_col='voucher', 
            #parse_dates=['expire_date'],
            header=0, 
            names=['voucher', 'value', 'expire_date', 'e_mail'])

mails = df.values.tolist()


def send_email(from_email, to_email, content, subject):
  """
    Envio um e-mail a partir de um e-mail de origem (necessário se conectar ao servidor do mesmo)
    from_email: dict com info do e-mail de origem
    to_email: e-mail de destino
    content: corpo do e-mail, conteúdo
    subject: assunto do e-mail
  """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email['e_mail']
    msg.set_content(content)
    
    msg['To'] = to_email
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(from_email['SMTP_SERVER'], from_email['PORT'])
        server.ehlo() 
        server.starttls(context=context) 
        server.ehlo() 
        server.login(msg["From"], from_email['PWD'])
        server.send_message(msg)
        logger.warning("Email enviado com sucesso de {} para {}".format(from_email['e_mail'], to_email))
        logger.debug(content)
    except Exception as e:
        logger.error(e)
    finally:
        server.quit() 
        
for index, e in enumerate(mails):
    content = """
Hey! Boas-vindas ao nosso primeiro Hackathon!\n
Para ajudar no processo criativo e deixar esse momento mais gostoso, preparamos um voucher do Ifood pra você! \U0001F609\n
Este é o seu código: {}\n
Para utilizar, abra o app do Ifood > Perfil > Pagamentos > Resgatar Ifood Card\n
Ele tem um saldo de R$ {} e é válido até {}. Aproveite!\n
          """.format(e[0], e[1], e[2])
    send_email(FROM, e[3], content, "Hackathon 2022 - Voucher iFood")
