from MongoDBAPI import DB


class User:
    name: str
    surname: str
    lastname: str
    age: int
    email: str
    busket_id: str


class Doctor:
    name: str
    surname: str
    lastname: str
    specialisation: str
    description: str

    def __str__(self):
        return f"{self.surname} {self.name} {self.lastname}"


class Tablets:
    name: str
    price: float
    description: str

    def __str__(self):
        return f"{self.name} - {self.price}P\n{self.description}"


class Basket:
    user_id: str
    items: list[str]


class Appeal:
    user_id: str
    doctor_id: str
    service_id: str
    time: str
    description: str


class Specialisation:
    name: str
    services: list


class Service:
    name: str
    price: float


if __name__ == '__main__':
    db = DB("Test")
    db.add_collection(User)
    db.add_collection(Basket)
    db.add_collection(Tablets)
    db.add_collection(Doctor)

    db.add_collection(Service)
    db.add_collection(Specialisation)

    db.add_collection(Appeal)

    '''
    db.Tablets.add(name="Эриус таблетки", price=699, description="5мг")
    db.Tablets.add(name="Кетотифен", price=119, description="1мг")
    db.Tablets.add(name="Эзлор СТ таблетки", price=429, description="5мг")
    db.Tablets.add(name="Диазолин таблетки", price=119, description="100мг")
    db.Tablets.add(name="Парацетамол таблетки шипучие", price=143, description="500мг")
    db.Tablets.add(name="Колдрекс Юниор порошок д/р-ра для приема внутрь", price=530, description="")
    db.Tablets.add(name="Ибупрофен суспензия д/приема внутрь апельсин", price=205, description="100мг")
    db.Tablets.add(name="Нормомед таблетки", price=1139, description="500мг")
    db.Tablets.add(name="Нео-ангин таблетки для рассасывания", price=269, description="")
    db.Tablets.add(name="Доритрицин таблетки для рассасывания", price=429, description="")
    db.Tablets.add(name="Риностейн спрей", price=359, description="")
    db.Tablets.add(name="Риномарис спрей", price=181, description="0.1%")
    db.Tablets.add(name="Гриппферон капли", price=307, description="10000МЕ/мл")
    db.Tablets.add(name="Арбидол капсулы", price=565, description="10мг")
    db.Tablets.add(name="Умифеновир-Озон капсулы", price=408, description="100мг")
    '''

    '''
    db.Service.add(name="Удаление зуба", price=900)
    db.Service.add(name="Установка пломбы", price=3000)
    db.Service.add(name="Ультразвуковая чистка", price=2500)
    db.Service.add(name="Первичная консультация", price=500)
    db.Service.add(name="Установка брекетов", price=15000)
    db.Service.add(name="Отбеливание", price=3000)
    db.Service.add(name="Удаление кариеса", price=3600)
    '''

    '''
    tooth_deletion = db.Service.find(name="Удаление зуба", price=900).id()
    seal_installing = db.Service.find(name="Установка пломбы", price=3000).id()
    tooth_cleaning = db.Service.find(name="Ультразвуковая чистка", price=2500).id()
    consult = db.Service.find(name="Первичная консультация", price=500).id()
    braces_installation = db.Service.find(name="Установка брекетов", price=15000).id()
    bleaching = db.Service.find(name="Отбеливание", price=3000).id()
    caries_removal = db.Service.find(name="Удаление кариеса", price=3600).id()

    db.Specialisation.add(name="Хирург",
                          services=[tooth_deletion, seal_installing, tooth_cleaning, bleaching, caries_removal])
    db.Specialisation.add(name="Педиатор", services=[consult])
    db.Specialisation.add(name="Ортодонт", services=[braces_installation, tooth_cleaning])
    db.Specialisation.add(name="Стоматолог-терапевт",
                          services=[consult, braces_installation, bleaching, caries_removal])
    db.Specialisation.add(name="Зубной врач", services=[consult])
    '''

    '''
    surgeon = db.Specialisation.find(name="Хирург").id()
    pediatrician = db.Specialisation.find(name="Педиатор").id()
    orthodontist = db.Specialisation.find(name="Ортодонт").id()
    dentist_therapist = db.Specialisation.find(name="Стоматолог-терапевт").id()
    dentist = db.Specialisation.find(name="Зубной врач").id()

    db.Doctor.add(name="Александр", surname="Джаббаров", lastname="Арсеньевич", specialisation=surgeon,
                  description="4.5")
    db.Doctor.add(name="Иван", surname="Лищенко", lastname="Владимирович", specialisation=pediatrician,
                  description="4.7")
    db.Doctor.add(name="Глеб", surname="Моисеев", lastname="Семёнович", specialisation=orthodontist, description="5.0")
    db.Doctor.add(name="Дмитрий", surname="Чернов", lastname="Павлович", specialisation=dentist_therapist,
                  description="4.2")
    db.Doctor.add(name="Олег", surname="Давыдов", lastname="Григорьевич", specialisation=dentist, description="4.6")
    '''
