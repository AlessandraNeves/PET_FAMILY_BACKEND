from sqlalchemy import Column, String, Integer, Float, UniqueConstraint
from sqlalchemy.orm import relationship

from  models import Base

class Pet(Base):
    __tablename__ = 'pet'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    birthday = Column(String(10), nullable=False) 
    domain = Column(String(10), nullable=False)
    gender = Column(String(1), nullable=False)
    breed = Column(String(30))
    weight = Column(Float)
    microchip = Column(Integer, unique=True)
    photo = Column(String())
    
        # Criando um requisito de unicidade envolvendo uma par de informações
    __table_args__ = (UniqueConstraint("microchip", name="pet_unique_id"),)

    def __init__(self, name:str, birthday:str, domain:str, gender:str, breed:str, weight:float, microchip:int, photo:str):
        """
        Cria o cadastro de um animal (Pet)

        Arguments:
            name: nome do animal
            birthday: data de nascimento
            domain: tipo do animal (cão, gato, ...)
            gender: sexo do animal (M, F)
            breed: raça do animal
            weight: peso do animal
            microchip: número do microchip implantado no animal
            photo: foto do animal
        """
        self.name = name
        self.birthday = birthday
        self.domain = domain
        self.gender = gender
        self.breed = breed
        self.weight = weight
        self.microchip = microchip
        self.photo = photo
