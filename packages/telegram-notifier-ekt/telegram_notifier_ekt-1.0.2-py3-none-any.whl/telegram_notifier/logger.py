import logging #Libreria para manejar un log
import os #Importar os para manejo de archivos y variables
from telegram_notifier_gremlam_ekt.utils import get_current_date_format

class InfoFilter():
    def filter(self, record):
        return record.levelname == "INFO"

def set_log(status:str, level:str):
    filemode = "a"
    date_today = get_current_date_format()
    file_name = r"C:\LOGTELEGRAM\r2tck_bot_" + str(date_today) + ".log"

    if not os.path.exists(r"C:\LOGTELEGRAM"):
        os.mkdir(r"C:\LOGTELEGRAM")

    logger = logging.getLogger(__name__) #Logging personalizado
    logger.setLevel(logging.DEBUG) #Establece el nivel inicial de los logs
    formatter = logging.Formatter(#Formato de salida de log
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger.handlers.clear() #Limpia los handlers de log

    console_h = logging.StreamHandler() #Mandar registros a la consola
    console_h.setLevel(logging.INFO) #Establecer nivel de importancia en filtros
    console_h.addFilter(InfoFilter()) #Establecer filtro personalizado estricto
    console_h.setFormatter(formatter) #Establece el formato de salida en log
    logger.addHandler(console_h) #Agrega handler a logger

    file_h = logging.FileHandler(file_name, filemode, encoding="utf-8") #Registrar file handler
    file_h.setLevel(logging.DEBUG) #Establecer nivel de importancia en filtros
    #file_h.addFilter() #Establecer filtro personalizado
    file_h.setFormatter(formatter) #Establecer formato de salida para el log
    logger.addHandler(file_h) #Registrar handler a logger

    if level == "DEBUG":
        logger.debug(status)

    if level == "INFO":
        logger.info(status)
    
    if level == "WARNING":
        logger.warning(status)

    if level == "ERROR":
        logger.exception(status)