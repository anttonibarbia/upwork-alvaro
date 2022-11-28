# Importar librerias
import traceback

# Importar funciones
import functions

# Importar y configurar logging para guardar registros de ejecuciones y errores.
import logging
logging.basicConfig(filename='scraper_1h.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def main():
    # Cargar diccionario de keywords
    keyword_dict = functions.load_keywords()

    # Definir timeframe
    timeframes = ['now 1-H']

    # Para cada grupo de keywords, realizamos busquedas en Trends y guardamos info en bbdd
    for key, value in keyword_dict.items():
        keywords = value
        functions.scrape_gtrends(keywords, timeframes, is_email_automation=False)


if __name__ == '__main__':
    # Dejar logging solo en caso de que ocurra un error.
    try:
        main()

    except Exception:
        logging.info(traceback.format_exc())