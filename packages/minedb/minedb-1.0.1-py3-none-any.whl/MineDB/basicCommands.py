class BasicCommands:

    #checks function attribute should be string
    def __checkIns(self, value=None, source=None):
        if value == None:
            value = []
        for v in value:
            if v == None:
                continue
            if not isinstance(v, str):
                raise ValueError(f"Error : valueError : {source} : Value should be string")
        return  True

    #checks attribute items lenght to prevent corruption
    def __checkItemLength(self, dbName, colName):
        if dbName not in self.existing_db:
            return False
        if colName not in self.existing_db[dbName]:
            return False

        collection = self.existing_db[dbName][colName]

        # empty collection is valid
        if not collection:
            return 0

        lengths = {
            len(field["items"])
            for field in collection.values()
        }

        if len(lengths) != 1:
            return False

        return lengths.pop()

#database commands

    def createDB(self,dbName:str):
        if not self.__checkIns([dbName], "createDB"):
            return
        checkName = dbName.isidentifier()
        if checkName == False:
            raise ValueError("Error : createDB : Invalid identifier")
        elif dbName in self.existing_db:
            raise ValueError("Error : createDB : Database is already exists")
        else:
            self.existing_db[dbName]={}
            return True

    def showDB(self,dbName:str=None):
        if not self.__checkIns([dbName], "showDB"):
            return
        if dbName != None:
            if dbName in self.existing_db:
                return True
            else:
                raise KeyError("Error : showDB : Database not exist")
        else:
            existingDB = []
            for db in self.existing_db.keys(): 
                existingDB.append(db)
            return existingDB
    
    def dropDB(self,dbName:str):
        if dbName == "sample":
            raise ValueError("MineDB : sample database is not dropable")
        if not self.__checkIns([dbName], "dropDB"):
            return
        if dbName not in self.existing_db:
            raise KeyError("Error : dropDB : Database not exist")
        self.existing_db.pop(dbName)
    
    def renameDB(self, dbName:str, newName:str):
        if not self.__checkIns([dbName, newName], "renameDB"):
            return
        if dbName == "sample":
            raise ValueError("MineDB : sample database is not renameable")
        tempDB = {}

        if dbName not in self.existing_db:
            raise KeyError("Error : renameDB : Database not exist")
        if newName in self.existing_db:
            raise ValueError("Error : renameDB : Database already exist")
        checkName = newName.isidentifier()
        if checkName != True:
            raise ValueError("Error : renameDB : Invalid identifier")
        for key, value in self.existing_db.items():
            if key == dbName:
                tempDB[newName] = value
            else:
                tempDB[key]=value
        self.existing_db = tempDB
        return True

#collection commands

    def createCollection(self,dbName:str,colName:str,**kwargs):
        if not self.__checkIns([dbName, colName], "createCollection"):
            return
        if dbName not in self.existing_db:
            raise KeyError("Error : alterFieldType : Database not exist")
        if colName in  self.existing_db[dbName]:
            raise ValueError("Error : alterFieldType : Collection already exist")
        checkName = colName.isidentifier()
        if checkName != True:
            raise ValueError("Error : createCollection : Invalid Identifier Of Attribute")
        temp = {}
        for key, value in kwargs.items():
            if key.isidentifier():
                if(value in ["text", "int", "float", "bool", "chr"]):
                    temp[key]={"dataType" : value, "items" : []}
                else:
                    raise ValueError(f"Error : createCollection : invalid data type it should be : {["text", "int", "float", "bool", "chr"]}")
            else:
                raise ValueError("Error : createCollection : Invalid Identifier Of Attribute")
        self.existing_db[dbName][colName]=temp
        return True

    def showCollection(self,dbName:str,colName=None):
        if not self.__checkIns([dbName,colName],"showCollection"):
            return
        if dbName not in self.existing_db:
            raise KeyError("Error : alterFieldType : Database not exist")
        if colName != None:
            if colName not in  self.existing_db[dbName]:
                raise KeyError("Error : alterFieldType : Collection not exist")
            collection = {colName : {}}
            for value in self.existing_db[dbName][colName]:
                collection[colName][value]=self.existing_db[dbName][colName][value]['dataType']
            return collection
        else:
            collection = {dbName:[]}
            for col in self.existing_db[dbName]:
                collection[dbName].append(col)
            return collection
    
    def dropCollection(self, dbName:str, colName:str):
        if not self.__checkIns([dbName,colName], "dropCollection"):
            return -1
        if dbName not in self.existing_db:
            raise KeyError("Error : alterFieldType : Database not exist")
        if colName not in  self.existing_db[dbName]:
            raise KeyError("Error : alterFieldType : Collection not exist")
        self.existing_db[dbName].pop(colName)
        return True
    
    def renameCollection(self, dbName:str, colName:str, newName:str):
        if not self.__checkIns([dbName, colName, newName], "renameCollection"):
            return
        tempCol = {}
        if dbName not in self.existing_db:
            raise KeyError("Error : alterFieldType : Database not exist")
        if colName not in  self.existing_db[dbName]:
            raise KeyError("Error : alterFieldType : Collection not exist")
        checkName = newName.isidentifier()
        if checkName != True:
            raise ValueError("Error : alterFieldType : Invalid identifier")
        for key, value in self.existing_db[dbName].items():
            if key == colName:
                tempCol[newName] = value
            else:
                tempCol[key]=value
        self.existing_db[dbName] = tempCol
        return True

 #Alter Commands

    def alterFieldType(self, dbName:str, colName:str, fieldName:str, dataType:str):
        if not self.__checkIns([dbName, colName, fieldName, dataType], "alterFieldType"):
            return
        if dbName not in self.existing_db:
            raise KeyError("Error : alterFieldType : Database not exist")
        if colName not in  self.existing_db[dbName]:
            raise KeyError("Error : alterFieldType : Collection not exist")
        if fieldName not in self.existing_db[dbName][colName]:
            raise KeyError("Error : alterFieldType : Field not exist")
        if dataType not in ["text", "int", "float", "bool", "chr"]:
            raise ValueError(f"Error : alterFieldType : invalid data type it should be : {["text", "int", "float", "bool", "chr"]}")
        
        field= self.existing_db[dbName][colName][fieldName]
        old_items = self.existing_db[dbName][colName][fieldName]["items"]
        def convert(v):
            if v is None:
                return None
            if dataType == "int":
                return int(v)
            if dataType == "float":
                return float(v)
            if dataType == "bool":
                return bool(v)
            if dataType == "text":
                return str(v)
            if dataType == "chr":
                s = str(v)
                if len(s) != 1:
                    raise ValueError("chr must be length 1")
                return s

        try:
            new_items = [convert(v) for v in old_items]
        except Exception:
            raise ValueError("alterFieldType: incompatible existing data")
        
        field["dataType"] = dataType
        field["items"] = new_items
        return True
    
    def alterFieldName(self, dbName:str, colName:str, fieldName:str, newName:str):
        if not self.__checkIns([dbName,colName,fieldName,newName], "alterFieldName"):
            return
        if dbName not in self.existing_db:
            raise KeyError("Error : alterFieldType : Database not exist")
        if colName not in  self.existing_db[dbName]:
            raise KeyError("Error : alterFieldType : Collection not exist")
        if fieldName not in self.existing_db[dbName][colName]:
            raise KeyError("Error : alterFieldType : Field not exist")
        tempFiled = {}
        checkName = newName.isidentifier()
        if checkName != True:
            raise ValueError("Error : alterFieldType : Invalid identifier")
        for key, value in self.existing_db[dbName][colName].items():
            if key == fieldName:
                tempFiled[newName] = value
            else:
                tempFiled[key] = value
        self.existing_db[dbName][colName] = tempFiled 
        return True
    
    def alterDropField(self, dbName:str, colName:str, fieldName:str):
        if not self.__checkIns([dbName, colName, fieldName]):
            return
        if dbName not in self.existing_db:
            raise KeyError("Error : alterDropField : Database not exist")
        if colName not in self.existing_db[dbName]:
            raise KeyError("Error : alterDropField : Collection not exist")
        if fieldName not in self.existing_db[dbName][colName]:
            raise KeyError("Error : alterDropField : Field not exist")
        self.existing_db[dbName][colName].pop(fieldName)
        
        return True

    def alterAddField(self, dbName:str, colName:str, fieldName:str, dataType:str):
        if not self.__checkIns([dbName, colName, fieldName],"alterAddField"):
            return
        if dbName not in self.existing_db:
            raise KeyError("Error : alterAddField : Database not exist")
        if colName not in self.existing_db[dbName]:
            raise KeyError("Error : alterAddField : Collection not exist")
        if fieldName in self.existing_db[dbName][colName]:
            raise ValueError("Error : alterAddField : Field already exist")
        if dataType not in ["text", "int", "float", "bool", "chr"]:
            raise ValueError(f"Error : alterAddField : invalid data type it should be : {["text", "int", "float", "bool", "chr"]}")
        length = self.__checkItemLength(dbName,colName)
        if length is False:
            raise RuntimeError("alterAddField: Internal schema corruption")
        self.existing_db[dbName][colName][fieldName]={"dataType":dataType,"items":[None]*length}
        
        return True