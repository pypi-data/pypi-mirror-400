import psycopg2
from sqlmodel import SQLModel, create_engine, Session
from utils.app_utils import AppUtils
from fastapi import status


class Database:

    def getEngine():
        # ########################################################################################
        # DB Connections
        # ########################################################################################

        if (
            AppUtils.getSettings().ENVIRONMENT.upper()
            == AppUtils.getEnvironment().dev.upper()
        ):
            DB_DEV_SERVER = AppUtils.getSettings().POSTGRES_HOST  # change
            DB_DEV_UID = AppUtils.getSettings().POSTGRES_USER
            DB_DEV_PASSWORD = AppUtils.getSettings().POSTGRES_PASS
            DB_DEV_NAME = AppUtils.getSettings().POSTGRES_DB
            DB_DEV_PORT = AppUtils.getSettings().POSTGRES_PORT
            conn = psycopg2.connect(
                host=DB_DEV_SERVER,
                port=DB_DEV_PORT,
                user=DB_DEV_UID,
                password=DB_DEV_PASSWORD,
                database=DB_DEV_NAME,
            )

            return create_engine(
                f"postgresql+psycopg2://{DB_DEV_UID}:{DB_DEV_PASSWORD}@{DB_DEV_SERVER}:{DB_DEV_PORT}/{DB_DEV_NAME}",
                creator=lambda: conn,
                pool_timeout=600,
            )
        elif (
            AppUtils.getSettings().ENVIRONMENT.upper()
            == AppUtils.getEnvironment().uat.upper()
        ):
            DB_UAT_SERVER = AppUtils.getSettings().POSTGRES_HOST  # change
            DB_UAT_UID = AppUtils.getSettings().POSTGRES_USER
            DB_UAT_PASSWORD = AppUtils.getSettings().POSTGRES_PASS
            DB_UAT_NAME = AppUtils.getSettings().POSTGRES_DB
            DB_UAT_PORT = AppUtils.getSettings().POSTGRES_PORT
            conn = psycopg2.connect(
                host=DB_UAT_SERVER,
                port=DB_UAT_PORT,
                user=DB_UAT_UID,
                password=DB_UAT_PASSWORD,
                database=DB_UAT_NAME,
            )

            return create_engine(
                f"postgresql+psycopg2://{DB_UAT_UID}:{DB_UAT_PASSWORD}@{DB_UAT_SERVER}:{DB_UAT_PORT}/{DB_UAT_NAME}",
                creator=lambda: conn,
                pool_timeout=600,
            )
        elif (
            AppUtils.getSettings().ENVIRONMENT.upper()
            == AppUtils.getEnvironment().prod.upper()
        ):
            DB_PROD_SERVER = AppUtils.getSettings().POSTGRES_HOST  # change
            DB_PROD_UID = AppUtils.getSettings().POSTGRES_USER
            DB_PROD_PASSWORD = AppUtils.getSettings().POSTGRES_PASS
            DB_PROD_NAME = AppUtils.getSettings().POSTGRES_DB
            DB_PROD_PORT = AppUtils.getSettings().POSTGRES_PORT

            conn = psycopg2.connect(
                host=DB_PROD_SERVER,
                port=DB_PROD_PORT,
                user=DB_PROD_UID,
                password=DB_PROD_PASSWORD,
                database=DB_PROD_NAME,
            )

            return create_engine(
                f"postgresql+psycopg2://{DB_PROD_UID}:{DB_PROD_PASSWORD}@{DB_PROD_SERVER}:{DB_PROD_PORT}/{DB_PROD_NAME}",
                creator=lambda: conn,
                pool_timeout=600,
            )
        else:
            return AppUtils.responseWithoutData(
                False, status.HTTP_200_OK, "Database connection failed"
            )

    def createDBTables():
        # ########################################################################################
        # Create table if doesn't exists
        # ########################################################################################
        SQLModel.metadata.create_all(Database.getEngine())

    # #########################################################################################
    # Session
    # #########################################################################################

    def getSession():
        session = Session(Database.getEngine())
        try:
            yield session
        finally:
            session.close()
