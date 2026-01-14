# app_utils.py
import base64
from enum import Enum
from datetime import datetime
import logging
import os
import re
import sys
from typing import Optional
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi_mail import ConnectionConfig, FastMail
from pydantic_settings import BaseSettings

from PIL import Image
import io


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    APIVERSION: Optional[str] = "1.0"
    POSTGRES_HOST: Optional[str]
    POSTGRES_PORT: Optional[str]
    POSTGRES_DB: Optional[str]
    POSTGRES_USER: Optional[str]
    POSTGRES_PASS: Optional[str]
    API_PORT: Optional[int] = 8000
    MAIL_USERNAME: Optional[str] = ""
    MAIL_PASSWORD: Optional[str] = ""
    MAIL_FROM: Optional[str] = ""
    MAIL_PORT: Optional[int] = 0
    MAIL_SERVER: Optional[str] = ""
    MAIL_FROM_NAME: Optional[str] = ""
    BASEURL_PROD: Optional[str] = ""
    BASEURL_UAT: Optional[str] = ""
    BASEURL_DEV: Optional[str] = ""
    AUTH_SECRET: Optional[str] = ""
    FIREBASE_CRED_TEST_PATH: Optional[str] = ""
    FIREBASE_CRED_LIVE_PATH: Optional[str] = ""
    SECRET_KEY: Optional[str] = ""
    AI_URL: Optional[str] = ""
    IMAGE_PATH: Optional[str] = ""
    DIFFICULTY_LEVEL: Optional[str] = ""
    IMAGE_DIFFICULTY_LEVEL: Optional[str] = ""
    STRIPE_WEBHOOK_SCERET: Optional[str] = ""
    VDOCIPHER_API_SECRET: Optional[str] = ""
    ANTHROPIC_API_KEY: Optional[str] = ""


class Environment(str, Enum):
    dev = "DEV"
    uat = "UAT"
    prod = "PROD"


class LogLevel(int, Enum):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class Role(str, Enum):
    user = "USER"
    superAdmin = "SUPER ADMIN"
    admin = "ADMIN"


class AppUtils:
    # Only methods
    def responseWithData(responseStatus, statusCode, message, responseData):
        data = {}
        data["status"] = responseStatus
        data["status_code"] = statusCode
        data["message"] = message
        data["data"] = responseData
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(data)
        )

    def responseWithoutData(responseStatus, statusCode, message):
        data = {}
        data["status"] = responseStatus
        data["status_code"] = statusCode
        data["message"] = message
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(data)
        )

    def getSettings() -> Settings:
        return Settings()

    def getEnvironment() -> Environment:
        return Environment

    def getLogLevel() -> LogLevel:
        return LogLevel

    def getRole() -> Role:
        return Role

    def mail_config():
        try:
            conf = ConnectionConfig(
                MAIL_USERNAME=AppUtils.getSettings().MAIL_USERNAME,
                MAIL_PASSWORD=AppUtils.getSettings().MAIL_PASSWORD,
                MAIL_FROM=AppUtils.getSettings().MAIL_FROM,
                MAIL_PORT=AppUtils.getSettings().MAIL_PORT,
                MAIL_SERVER=AppUtils.getSettings().MAIL_SERVER,
                MAIL_FROM_NAME=AppUtils.getSettings().MAIL_FROM_NAME,
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
                TEMPLATE_FOLDER=f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/templates",
            )
            AppUtils.logger(
                __name__, AppUtils.getLogLevel().INFO, f"mail cconfig == {conf}"
            )
            return conf
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            AppUtils.logger(
                __name__,
                AppUtils.getLogLevel().ERROR,
                f"mail config line no: {exc_tb.tb_lineno} | {ex}",
            )

    async def sendEmail(message, template_name):
        try:
            AppUtils.logger(
                __name__,
                AppUtils.getLogLevel().INFO,
                f"email template = {template_name}",
            )
            fm = FastMail(AppUtils.mail_config())
            AppUtils.logger(__name__, AppUtils.getLogLevel().INFO, f"config == {fm}")
            await fm.send_message(message, template_name=template_name)
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            AppUtils.logger(
                __name__,
                AppUtils.getLogLevel().ERROR,
                f"line no: {exc_tb.tb_lineno} | {ex}",
            )

    def setup_logger(name, fileName, level=logging.ERROR) -> logging.Logger:
        FORMAT = "[%(levelname)s  %(name)s %(module)s:%(lineno)s - %(funcName)s() - %(asctime)s]\n\t %(message)s \n"
        TIME_FORMAT = "%d.%m.%Y %I:%M:%S %p"
        if AppUtils.getSettings().ENVIRONMENT == AppUtils.getEnvironment().dev:
            FILENAME = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), fileName
            )
        else:
            current_dir = os.path.dirname(__file__)
            FILENAME = os.path.join(current_dir, fileName)
            # FILENAME = f"/home/atl_014/Desktop/investaa/api/utils/{fileName}"
        # else:
        #     FILENAME = f"/home/Projects/investabackend/utils/{fileName}"

        logging.basicConfig(
            format=FORMAT,
            datefmt=TIME_FORMAT,
            level=level,
            force=True,
            encoding="utf-8",
            filename=FILENAME,
            filemode="a",
        )

        logger = logging.getLogger(name)
        return logger

    def logger(name, level: int, message: str):
        fileName = f"serverlog_{datetime.now().strftime('%Y-%m-%d')}.log"
        logger = AppUtils.setup_logger(name, fileName, level=level)
        logger.log(level=level, msg=message)

    def encodeData(value):
        encodeValue = value.encode("ascii")
        bencode = base64.b64encode(encodeValue)
        encodeData = bencode.decode("ascii")
        return encodeData

    def getCurrentDateTime():
        currentDateTime = datetime.now()
        return currentDateTime

    def Baseurl():
        if AppUtils.getSettings().ENVIRONMENT == AppUtils.getEnvironment().dev:
            BASEURL = AppUtils.getSettings().BASEURL_DEV
        elif AppUtils.getSettings().ENVIRONMENT == AppUtils.getEnvironment().uat:
            BASEURL = AppUtils.getSettings().BASEURL_UAT
        else:
            BASEURL = AppUtils.getSettings().BASEURL_PROD
        return BASEURL

    def format_duration(duration):
        AppUtils.logger(
            __name__,
            AppUtils.getLogLevel().INFO,
            f"Received duration: {duration} (type: {type(duration)})",
        )

        if isinstance(duration, str):
            # If it's already in "X.XX minutes" format, extract the number
            match = re.match(r"([\d.]+) minutes", duration)
            if match:
                duration = float(match.group(1))  # Convert extracted number to float

            elif ":" in duration:  # Handle "HH:MM" format
                try:
                    hours, minutes = map(int, duration.split(":"))
                    return f"{hours + (minutes / 60):.2f} minutes"
                except ValueError:
                    return f"{duration} minutes"  # Fallback

        if isinstance(duration, (int, float)):  # Handle numeric durations
            return f"{float(duration):.2f} minutes"

        return f"Invalid duration: {duration}"

    def compress_image(image_path, quality=50, max_size_kb=400):
        """Compress the image to be under max_size_kb (400 KB)."""
        AppUtils.logger(__name__, AppUtils.getLogLevel().INFO, "Compressing image...")

        with Image.open(image_path) as img:
            img = img.convert("RGB")  # Ensure compatibility
            compressed_io = io.BytesIO()

            # Initial compression
            img.save(compressed_io, format="JPEG", quality=quality)
            file_size_kb = compressed_io.tell() / 1024  # Convert bytes to KB
            AppUtils.logger(
                __name__,
                AppUtils.getLogLevel().INFO,
                f"Initial size: {file_size_kb} KB",
            )

            # Adjust quality and resize iteratively if necessary
            while file_size_kb > max_size_kb and quality > 10:
                quality -= 10  # Reduce quality in steps
                compressed_io = io.BytesIO()
                img.save(compressed_io, format="JPEG", quality=quality)
                file_size_kb = compressed_io.tell() / 1024  # Update file size

            # If still too large, resize the image
            scale_factor = 0.9  # Reduce by 10% each time
            while file_size_kb > max_size_kb and scale_factor > 0.3:
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                img = img.resize((new_width, new_height), Image.ANTIALIAS)

                compressed_io = io.BytesIO()
                img.save(compressed_io, format="JPEG", quality=quality)
                file_size_kb = compressed_io.tell() / 1024  # Update file size
                scale_factor -= 0.1

            AppUtils.logger(
                __name__, AppUtils.getLogLevel().INFO, f"Final size: {file_size_kb} KB"
            )
            return compressed_io.getvalue()
