import os
import sys

from src.CustomException import CustomException
from src.logger import logger
from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

@dataclass
class DataIngestionConfig:

    train_data_path:str = os.path.join(os.getcwd(),'data','train.csv')
    test_data_path:str = os.path.join(os.getcwd(),'data','test.csv')
    
class DataIngestion:

    def __init__(self):

        self.ingestion_config = DataIngestionConfig()

    def initiate_ingestion(self):

        try:

            logger.info('data ingestion has started')

            raw_data_path = r'C:\Users\gomes\OneDrive\Gomes Data Science\House pricing noida web scrap\EDA\property_data.csv'
            data_frame = pd.read_csv(raw_data_path)

            os.makedirs(self.ingestion_config.train_data_path)

            train_data,test_data = train_test_split(data_frame,test_size=0.2,random_state=42)

            train_data.to_csv(self.ingestion_config.train_data_path,index=False,header = True)
            test_data.to_csv(self.ingestion_config.test_data_path,index=False,header = True)
        
            logger.info('Data ingestion has been completed')

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.train_data_path
            )
        except Exception as e:
            raise CustomException(e,sys)
    
if __name__ == "__main__":
    x = DataIngestion().initiate_ingestion()



