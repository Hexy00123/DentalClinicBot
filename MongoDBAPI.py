import pymongo
from config import CONNECTION_STRING


class DataClass(object):
    def __init__(self, inst, collection):
        self.__inst = inst
        self.__collection: Collection = collection
        self.__is_changed = False
        self.__id: str

    def __getattr__(self, item):
        try:
            return self.__dict__.__getitem__(item)
        except KeyError:
            return self.__inst.__getattribute__(item)

    def __setattr__(self, key, value):
        if key.startswith('_DataClass'):
            super().__setattr__(key, value)
        else:
            super().__setattr__("_DataClass__is_changed", True)

            if self.__id in self.__collection.updates:
                self.__collection.updates[self.__id].append((key, value))
            else:
                self.__collection.updates[self.__id] = [(key, value)]

            setattr(self.__inst, key, value)

    def is_changed(self) -> bool:
        return self.__is_changed

    def id(self) -> str:
        return self.__id

    def __str__(self):
        if (str(self.__inst).startswith("<") and str(self.__inst).endswith(">")):
            res = f"{type(self.__inst).__name__}: {'{'}"
            for field, annotation in self.__inst.__annotations__.items():
                try:
                    field_value = getattr(self.__inst, field)
                    res += f"{field}: {field_value}"
                except AttributeError:
                    res += f"{field}: {None}"
                res += ", "
            res = res[:-2] + "}"
            return res
        return str(self.__inst)

    def __repr__(self):
        return str(self)


class Collection():
    def __init__(self, db, collection, data_type: type):
        if type(data_type) != type:
            raise TypeError("You must provide a type, pass a data-class as an argument")
        self.db = db
        self.collection: pymongo.collection.Collection = collection
        self.data_type: type = data_type
        self.updates: dict = {}
        self.acceptable_types = [int, float, str, tuple, list, dict]

        self.data_type.__annotations__["_id"] = str

    def __db_object2data_class(self, obj: dict):
        try:
            instance = self.data_type()
            for field in self.data_type.__annotations__:
                if field in obj:
                    instance.__setattr__(field, obj[field])
                else:
                    instance.__setattr__(field, None)
            res = DataClass(instance, self)
            res._DataClass__id = obj["_id"]
        except TypeError:
            params = {}
            for field in self.data_type.__annotations__:
                if field in obj:
                    params[field] = obj[field]
                else:
                    params[field] = None
            res = DataClass(self.data_type(**params), self)
            res._DataClass__id = obj["_id"]
        return res

    def add(self, *args, **kwargs):
        to_send = dict()

        if len(args) == 1:
            obj = args[0]
            if type(obj) == self.data_type:
                for field in obj.__annotations__:
                    if obj.__annotations__[field] in self.acceptable_types:
                        if field in self.data_type.__annotations__:
                            to_send[field] = obj.__getattribute__(field)
                        else:
                            raise AttributeError(f"Provided dataclass does not have field: {field}")
                    else:
                        print(f"MONGODBAPI:\n\trejected: {obj.__annotations__[field]}, {field}")
        elif kwargs:
            for field in kwargs:
                if type(kwargs[field]) in self.acceptable_types:
                    if field in self.data_type.__annotations__:
                        to_send[field] = kwargs[field]
                    else:
                        raise AttributeError(f"Provided dataclass does not have field: {field}")
                else:
                    print(f"MONGODBAPI:\n\trejected: {type(kwargs[field])}, {field}")

        print(to_send)
        self.collection.insert_one(to_send)

    def find(self, **kwargs):
        request = self.collection.find_one(kwargs)
        if request:
            return self.__db_object2data_class(request)
        return None

    def get_all_instances(self):
        res = []
        for obj in list(self.collection.find().__iter__()):
            res.append(self.__db_object2data_class(obj))
        return res

    def commit(self):
        for key in self.updates:
            for field_update in self.updates[key]:
                self.collection.find_one_and_update({"_id": key}, {"$set": {field_update[0]: field_update[1]}})
        self.updates = dict()

    def __iter__(self):
        return self.get_all_instances().__iter__()


class DB():
    def __init__(self, name: str):
        self.client = pymongo.MongoClient(CONNECTION_STRING)
        self.db = self.client.get_database(name)
        self.collections: dict[str: Collection] = {}
        self.collection_names: list[str] = [c["name"] for c in self.db.list_collections()]

    def add_collection(self, data_type: type):
        if data_type.__name__ not in self.collection_names:
            print(f"Creating collection: {data_type.__name__}")
            self.db.create_collection(data_type.__name__)

        self.collections[data_type.__name__] = Collection(self, self.db.get_collection(data_type.__name__),
                                                          data_type)
        self.__dict__[data_type.__name__]: Collection = self.collections[data_type.__name__]
