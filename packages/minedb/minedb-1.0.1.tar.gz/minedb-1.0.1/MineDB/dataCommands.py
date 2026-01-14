class DataCommands:

#datatype and value validation commands

    #checks function attribute should be string
    def __checkIns(self, value, source=None):
        for v in value:
            if v == None:
                continue
            if not isinstance(v, str):
                raise ValueError(f"Error : valueError : {source} : Value should be string")
        return  True

    #checks for loading/modifing value datatype
    def __checkValueType(self, value, source=None):
        if isinstance(value,str):
            if len(value) > 1:
                return "text"
            else:
                return "chr"
        elif isinstance(value,bool):
            return 'bool'
        elif isinstance(value,int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        else:
            raise ValueError(f"Error : {source} : Invalid data type of value {value}")

    #checking valiadation of loading/modifing data
    def __checkValue(self, loadData, source=None):
        for key, value in loadData.items():
            if key in self.existing_db[self.currDB][self.currColl]:
                if value == None or value == "None":
                    continue
                if self.__checkValueType(value,source) != self.existing_db[self.currDB][self.currColl][key]["dataType"]:
                    raise ValueError(f"Error : {source} : Invalid data type of value {value}")
            else:
                raise KeyError(f"Error : {source} : Field not exist")
        return True

#get and set commands
    def getDB(self):
        return self.currDB

    def getCollection(self):
        return self.currColl

    def setDB(self, dbName):
        if not self.__checkIns([dbName],"setDB"):
            return
        if dbName.isidentifier():
            if dbName in self.existing_db:
                self.currDB = dbName
            else:
                raise KeyError("Error : setDB : Database not exist")
        else:
            raise ValueError("Error : setDB : Invalid identifier")

    def setCollection(self, colName):
        if not self.__checkIns([colName],"setCollection"):
            return
        if colName.isidentifier():
            if colName in self.existing_db[self.currDB]:
                self.currColl = colName
            else:
                raise KeyError("Error : setCollection : Collection not exist")
        else:
            raise ValueError("Error : setCollection : Invalid identifier")

#major data commands
    def load(self, **kwargs):
        if len(self.existing_db[self.currDB][self.currColl]) == len(kwargs):
            if not self.__checkValue(kwargs,"load"):
                return
            for key, value in kwargs.items():
                self.existing_db[self.currDB][self.currColl][key]['items'].append(value)
            return True
        else:
            raise ValueError("Error : load : Incomplete loading")

    def modify(self, search_by, search_value, update_field, new_value):
        collection = self.existing_db[self.currDB][self.currColl]

        # validate fields and value types
        self.__checkValue(
            {search_by: search_value, update_field: new_value},
            "modify"
        )

        value_array = collection[search_by]["items"]

        # find matching row indexes
        indexes = [
            i for i, v in enumerate(value_array)
            if v == search_value
        ]

        if not indexes:
            raise ValueError("modify: search_value not exist")

        # update all matching rows
        for i in indexes:
            collection[update_field]["items"][i] = new_value

        return True

    def remove(self, search_by, search_value):
        collection = self.existing_db[self.currDB][self.currColl]

        # validate search field and value type
        self.__checkValue({search_by: search_value}, "remove")

        value_array = collection[search_by]["items"]

        # find all matching indexes
        indexes = [
            i for i, v in enumerate(value_array)
            if v == search_value
        ]

        if not indexes:
            raise ValueError("remove: search_value not exist")

        # remove from highest index to lowest (no drift)
        for i in reversed(indexes):
            for field in collection:
                collection[field]["items"].pop(i)

        return True

    def explore(self,*args):
        exp = {}
        for value in args:
            if value in self.existing_db[self.currDB][self.currColl]:
                exp[value]=self.existing_db[self.currDB][self.currColl][value]["items"]
            else:
                raise KeyError("Error : explore : Field not exist")
        return exp
    
    def exploreAll(self):
        try:
            exp={}
            for value in self.existing_db[self.currDB][self.currColl]:
                exp[value]=self.existing_db[self.currDB][self.currColl][value]["items"]
            return exp
        except(TypeError, KeyError) as e:
            raise RuntimeError("Error : exploreAll : something went wrong, check setup of database and column") from e