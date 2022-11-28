# Importar librerias
from pytrends.request import TrendReq
from sqlalchemy import create_engine
import pandas as pd
import datetime
import time
import os
import logging


# Importar librerias de emails
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Importar credenciales
import creds


# Definimos funciones que se van a ejecutar desde scripts


# Funcion para cargar diccionario con keywords principales y asociadas
def load_keywords():

    # Separador del txt de diccionario de keywords
    separador = ';'

    with open(os.path.join(os.getcwd(), 'diccionario_keywords.txt'), 'r') as file:
        lines = [line.rstrip().strip().lower() for line in file]
        keywords = [line.split(separador) for line in lines if line]
    
    keyword_dict = {}
    for keyword_group in keywords:
        keyword_dict[keyword_group[0]] = keyword_group

    return keyword_dict



# Funcion para enviar emails con resultados
def send_email_results(keywords, now_date):

    with open(os.path.join(os.getcwd(), 'tails_table.html'), 'r') as file:
        tails_html = file.read()

    subject = f"Resultados Google Trends - {keywords[0].title()} - {now_date}"
    text = '5 últimos registros para cada una de las keywords:'
    sender_email = "scraping.robot1@gmail.com"
    recipients = ["antton.ibarbia@gmail.com", "antton_1414@hotmail.com"]

    # Crear mensaje multipart y definir headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    # Añadir body al email
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(tails_html, "html"))

    filename = f'resultados_grupo_{keywords[0]}_{now_date}.csv'

    # Abrir archivo para adjuntar y definir su encoding y headers
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Añadir archivo adjunto al email y cargar texto como string
    message.attach(part)

    # Logear al servidor con contexto seguro y enviar email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, creds.pass_email)
        server.sendmail(sender_email, recipients, message.as_string())

    logging.info(f'Emails de resultados enviados.')



# Funcion para enviar emails con resultados
def send_email_no_results(keyword):

    subject = f"No resultados para keyword {keyword}"
    text = f'Google Trends no tiene información sobre keyword {keyword}'
    sender_email = "scraping.robot1@gmail.com"
    recipients = ["antton.ibarbia@gmail.com", "antton_1414@hotmail.com"]

    # Crear mensaje multipart y definir headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    # Añadir body al email
    message.attach(MIMEText(text, "plain"))

    # Logear al servidor con contexto seguro y enviar email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, creds.pass_email)
        server.sendmail(sender_email, recipients, message.as_string())



# Funcion para extraer la informacion de Trends
def scrape_gtrends(keywords, timeframes, is_email_automation):

    logging.info(f'Busquedas de Trends para keywords: {keywords}')

    # Definir pytrends
    pytrends = TrendReq(timeout=(15,40), retries=2, backoff_factor=0.1)

    # Definir parametros de búsqueda (excepto timeframe)
    category = '7'              # finanzas
    geo = ''                    # default: todo el mundo
    gprop = ''                  # default: busquedas web

    # Si no es para email, crear conexion a la bbdd MySQL
    if is_email_automation == False:
        engine = create_engine("mysql+pymysql://" + creds.user_mysql + ":" + creds.pass_mysql + "@" + creds.host_mysql + "/" + creds.db_mysql)
    
    # Crear listas para añadir dataframes y ultimos 5 registros de cada uno.
    df_list = []
    df_tail_list = []

    # Bucle para realizar busqueda de Trends y guardar info en SQL para cada keyword
    
    for keyword in keywords:
        
        keyword_list = [keyword]

        for timeframe in timeframes:
            try:
                # Cargar pytrends con parametros
                pytrends.build_payload(keyword_list, category, timeframe, geo, gprop)

                # Realizar busqueda y sacar resultados a dataframe de pandas
                df = pytrends.interest_over_time()
                
            except Exception as e:
                logging.info(f'Error - PyTrends no funciono correctamente para timeframe "{timeframe}" y keyword "{keyword}".')
                logging.info(f'----> Detalle error: {e}')
                continue
            
            # Si Trends no da datos, enviar correo informando de ello y pasar a siguiente keyword.
            if len(df) == 0:
                logging.info(f'No hay resultados de Trends para kewyord: "{keyword}".')
                send_email_no_results(keyword, is_keyword_undefined=False)
                break

            else:
                # Eliminar dato de la ultima hora (inestable)
                # df = df[:-1]

                # Cambiar a hora española y pasar index a columna normal
                df.index = df.index + datetime.timedelta(hours=1)
                df.index = df.index.strftime('%Y-%m-%d %H:%M:%S')
                df = df.reset_index()

                # Eliminar columna auxiliar isPartial
                df = df.drop(columns=['isPartial'])

                # Renombrar columnas
                df.columns = ['datetime', 'volume']

                # Añadir columnas con timeframe y keyword
                df.insert(0, 'timeframe', timeframe)
                df.insert(0, 'keyword', keyword)

                # Registrar hora de ejecucion y añadir columna
                now_datetime = datetime.datetime.now()
                exec_time = now_datetime.strftime("%Y-%m-%d %H:%M:%S")
                df.insert(0, 'execution_timestamp', exec_time)

                # Añadir df completo y ultimos 5 registros a listas de dfs
                df_list.append(df)
                df_tail_list.append(df.tail(5))

                # Esperamos 3s antes de pasar a siguiente keyword para no saturar el servidor
                #time.sleep(3)
        
                logging.info(f'Ok - Informacion de Trends de timeframe "{timeframe}" extraida para keyword: "{keyword}".')

    if len(df_list) > 0:
        df_all = pd.concat(df_list, ignore_index=True)
        df_tail_all = pd.concat(df_tail_list, ignore_index=True)
    else:
        logging.info(f'Error - Pytrends no devolvió ningun resultado para el grupo de keywords.')

    # Si no es para email, guardar df en bbdd MySQL
    if is_email_automation == False:
        df_all.to_sql('keyword_volumes', engine, if_exists='append', index=False)

    # Si es para email, guardar df en csv y tails en html
    elif is_email_automation == True:
        now_date = now_datetime.strftime("%Y%m%d")
        df_all.to_csv(os.path.join(os.getcwd(), f'resultados_grupo_{keywords[0]}_{now_date}.csv'), index=False)
        df_tail_all.to_html(os.path.join(os.getcwd(), 'tails_table.html'), index=False)

        return now_date
