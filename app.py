from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import strawberry

from sqlalchemy import select, delete

from typing import List, Optional

import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins='[*]',
    allow_methods='[*]',
    allow_headers='[*]',
    allow_credentials=True
)

@strawberry.type
class Pet:
    id: strawberry.ID
    name: str
    birthday: str
    domain: str
    gender: str
    breed: str
    weight: float
    microchip: int
    photo: str
   
    @classmethod
    def marshal(cls, model: models.Pet) -> "Pet":
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name,
            birthday=model.birthday,
            domain=model.domain,
            gender=model.gender,
            breed=model.breed,
            weight=model.weight,
            microchip=model.microchip,
            photo=model.photo
        )

@strawberry.input
class PetDataInput: 
    name: str = None
    birthday: str = None
    domain: str = None
    gender: str = None
    breed: str = None
    weight: float = None
    microchip: int = None
    photo:str = None

@strawberry.input
class PetQueryInput:
    termo: Optional[str] = strawberry.UNSET

@strawberry.type
class PetExists:
    message: str = "Pet de mesmo nome já inserido na base"

@strawberry.type
class PetNotFound:
    message: str = "Não foi possível encontrar o pet"

@strawberry.type
class PetRemoveMessage:
    message: str = "Pet removido com sucesso"

PetResponse = strawberry.union("PetResponse", (Pet, PetExists, PetNotFound, PetRemoveMessage))

@strawberry.type
class Query:

    @strawberry.field
    async def all_pets(self) -> List[Pet]:
        async with models.get_session() as session:
            sql = select(models.Pet).order_by(models.Pet.name)
            db_pets = (await session.execute(sql)).scalars().unique().all()

        #return [Pet.marshal(pet) for pet in db_pets]
        return db_pets

            
    @strawberry.field
    async def search_pet(self, query_input: Optional[PetQueryInput] = None) -> List[Pet]:
        async with models.get_session() as session:
            if query_input:
                sql = select(models.Pet) \
                        .filter(models.Pet.name.ilike(f"%{query_input.termo}%")).\
                            order_by(models.Pet.name)
            else:
                sql = select(models.Pet).order_by(models.Pet.name)

            db_pets = (await session.execute(sql)).scalars().unique().all()

        return [Pet.marshal(pet) for pet in db_pets]

@strawberry.type
class Mutation:

    @strawberry.field
    async def add_pet(self, name: str, birthday: str, domain: str, gender: str, 
                      breed: str, weight: float, microchip: int, photo: str) -> PetResponse: 
        async with models.get_session() as session:

            sql = select(models.Pet).\
                filter(models.Pet.microchip == microchip)
            db_pet_exists = (await session.execute(sql)).scalars().unique().all()

            if db_pet_exists:
                return PetExists()

            db_pet = models.Pet(name=name, birthday=birthday, domain=domain, gender=gender, 
                                breed=breed, weight=weight, microchip=microchip, photo=photo)
            session.add(db_pet)
            await session.commit()

        return Pet.marshal(db_pet)

    @strawberry.field
    async def edit_pet(self, id: int, edits: PetDataInput) -> PetResponse: 
        async with models.get_session() as session:

            sql = select(models.Pet).\
                filter(models.Pet.id == id)
            db_pet_exists = (await session.execute(sql)).scalars().first()

            if not db_pet_exists:
                return PetNotFound()
            
            if edits.name != None: db_pet_exists.name = edits.name
            if edits.birthday != None: db_pet_exists.birthday = edits.birthday
            if edits.domain != None: db_pet_exists.domain = edits.domain
            if edits.gender != None: db_pet_exists.gender = edits.gender
            if edits.breed != None: db_pet_exists.breed = edits.breed
            if edits.weight != None: db_pet_exists.weight = edits.weight
            if edits.microchip != None: db_pet_exists.microchip = edits.microchip
            if edits.photo != None: db_pet_exists.photo = edits.photo
            
            await session.commit()

        return Pet.marshal(db_pet_exists)

    @strawberry.field
    async def remove_pet(self, id: int) -> PetResponse: 
        async with models.get_session() as session:

            sql = select(models.Pet).filter(models.Pet.id == id)
            db_pet_exists = (await session.execute(sql)).scalars().first()

            if not db_pet_exists:
                return PetNotFound()
            
            session.delete(db_pet_exists)
            await session.commit()

        return PetRemoveMessage()

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")