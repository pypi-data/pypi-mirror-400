from .basicCommands import BasicCommands
from .dataCommands import DataCommands
from cryptography.fernet import Fernet
import json
import os
class MineDB(BasicCommands, DataCommands):

    def __init__(self):
        self.version = "1.0.1"
        self.existing_db={"sample":{"data":{"version":"1.1v","developer":"hrs_developers"}}}
        self.currDB = "sample"
        self.currColl = "data"

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.__path = os.path.join(base_dir, "secure.dat")
        self.__key_path = os.path.join(base_dir, "MineDBKey.key")

        os.makedirs(base_dir, exist_ok=True)

        #checking for key
        #if present load
        if os.path.exists(self.__key_path):
            with open(self.__key_path, "rb") as f:
                key = f.read()
        #if not present create
        else:
            key = Fernet.generate_key()
            with open(self.__key_path, "wb") as f:
                f.write(key)

        self.__cipher = Fernet(key)

        #checking for exsting_db
        #if present load
        if os.path.exists(self.__path):
            with open(self.__path, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.__cipher.decrypt(encrypted_data)
            self.existing_db = json.loads(decrypted_data)
        #if not present create with sample
        else:
            self.existing_db = {
                "sample": {
                    "data": {
                        "version": self.version,
                        "developer": "hrs_developers"
                    }
                }
            }
            self.save()    

    def save(self):
        json_data = json.dumps(self.existing_db).encode()
        encrypted_data = self.__cipher.encrypt(json_data)
        with open(self.__path,"wb") as f:
            f.write(encrypted_data)