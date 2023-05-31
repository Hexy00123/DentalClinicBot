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
        return f"{self.surname} {self.name} {self.lastname}\nСпециализация: {self.specialisation}"


class Tablets:
    name: str
    price: float
    description: str

    def __str__(self):
        return f"{self.name} - {self.price}P\n{self.description}"


class Basket:
    user_id: str
    items: list[str]


class BasketHistory:
    ...


class Appeal:
    user_id: str
    doctor_id: str


if __name__ == '__main__':
    db = DB("Test")
    db.add_collection(User)
    db.add_collection(Basket)
    db.add_collection(Tablets)
    db.add_collection(Doctor)

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
    db.Doctor.add(name="Александр", surname="Джаббаров", lastname="Арсеньевич", specialisation="Хирург",
                  description="4.5")
    db.Doctor.add(name="Иван", surname="Лищенко", lastname="Владимирович", specialisation="Педиатор", description="4.7")
    db.Doctor.add(name="Глеб", surname="Моисеев", lastname="Семёнович", specialisation="Мед-брат", description="5.0")
    db.Doctor.add(name="Дмитрий", surname="Чернов", lastname="Павлович", specialisation="Ортодонт", description="4.2")
    db.Doctor.add(name="Олег", surname="Давыдов", lastname="Григорьевич", specialisation="Окулист", description="4.6")
    '''
