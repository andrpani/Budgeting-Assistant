import os
import json
import base64
import sqlite3
from dotenv import load_dotenv
from collections import namedtuple
from datamodel import StructuredData
from langchain.chat_models import init_chat_model
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage

load_dotenv()

def custom_json_decoder(json_dict):
    return namedtuple('Configuration', json_dict.keys())(*json_dict.values())


def extract_from_receipt(dir_path: str):
    print(os.listdir(dir_path))



if __name__ == '__main__':
    with open('config.json', 'r') as jsonfile:
        config = json.load(jsonfile, object_hook=custom_json_decoder)
        llm = init_chat_model(config.llm.model, model_provider=config.llm.model_provider)
        files = os.listdir(config.input_dir)
        llm_structured = llm.with_structured_output(StructuredData)
        all_purchases = []
        #parser = PydanticOutputParser(pydantic_object=StructuredData)
        for filename in files:
            with open(os.path.join(config.input_dir, filename), "rb") as f:
                encoded_file = base64.b64encode(f.read()).decode("utf-8")
                if filename.endswith('pdf'):
                    message = HumanMessage(
                        content=[
                            {"type": "text", "text": "Describe the local pdf file"},
                            {
                                "type": "file",
                                "source_type": "base64",
                                "data": encoded_file,
                                "mime_type": "application/pdf",
                            }
                        ]
                    )
                    extracted_data = llm_structured.invoke([message])
                    #print(purchases, '\n\n')
                    all_purchases.extend(extracted_data.purchases)
                elif filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                    extension = filename.replace('jpg', 'jpeg').split('.')[-1]
                    message = HumanMessage(
                        content=[
                            {"type": "text", "text": "Describe the local image"},
                            {
                                "type": "image",
                                "source_type": "base64",
                                "data": encoded_file,
                                "mime_type": f"image/{extension}",
                            }
                        ]
                    )
                    purchases = llm_structured.invoke([message])
                    #print(purchases, '\n\n')
                    all_purchases.extend(extracted_data.purchases)
    
    print(all_purchases)
    
    # save into the db
    with sqlite3.connect('budgeting.db') as db_connection:
        cursor = db_connection.cursor()
        # insert the purchases and items
        for purchase in all_purchases:
            purchase_dict = purchase.model_dump()
            del purchase_dict['items']
            cursor.execute("INSERT INTO Purchase(Title, Date, Total) " \
                                        "VALUES (:title, :date, :total)", purchase_dict)
            db_connection.commit()
            purchase_id = cursor.lastrowid
            for item in purchase.items:
                item_dict = item.model_dump()
                item_dict['purchase_id'] = purchase_id
                cursor.execute("INSERT INTO PurchaseItem(Name, Quantity, UnitPrice, TotPrice, Info, PurchaseID)" \
                                    "VALUES (:name, :quantity, :unit_price, :tot_price, :info, :purchase_id)", item_dict)
                db_connection.commit()