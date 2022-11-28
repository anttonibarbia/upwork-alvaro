# Importar librerias
import traceback
import os
import imaplib, email
from email import policy

# Importar credenciales y funciones
import config
import functions

# Importar y configurar logging para guardar registros de ejecuciones y errores.
import logging
logging.basicConfig(filename='scraper_email.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


# Funcion principal con la logica del proceso
def main(): 

    keyword_dict = functions.load_keywords()

    # Lista de timeframes para los que se van ha hacer busquedas: ultimas 1h, 4h y 24h.
    timeframes = config.timeframes_scraper_email

    # Iniciar conexion imap
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login(config.user_email, config.pass_email)

    # Seleccionar mensajes sin leer del inbox
    mail.select('Inbox')
    status, data = mail.search(None, '(UNSEEN)')

    # Para cada uno de los mensajes nuevos, leer asunto y ejecutar procesos si tenemos 'venta de' en el asunto
    for num in data[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        email_msg = data[0][1]
        email_msg = email.message_from_bytes(email_msg, policy=policy.SMTP)
        subject = str(email_msg['Subject']).lower()

        if 'venta de' in subject:

            keyword = subject.split('venta de ')[1].strip()

            logging.info(f'Email detectado con keyword: {keyword}')

            try:
                keywords = keyword_dict[keyword]
            except:
                keywords = [keyword]
            
            now_date = functions.scrape_gtrends(keywords, timeframes, is_email_automation=True)
            functions.send_email_results(keywords, now_date)
    
            # Borrar archivos temporales
            os.remove(os.path.join(os.getcwd(), f'resultados_grupo_{keywords[0]}_{now_date}.csv'))
            os.remove(os.path.join(os.getcwd(), 'tails_table.html'))


if __name__ == '__main__':
    # Habilitar logging
    logging.disable(logging.NOTSET)
    try:
        main()

    except Exception:
        logging.info(traceback.format_exc())