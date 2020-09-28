from typing import List

import databases
import sqlalchemy
import os
import urllib.parse
import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from sqlalchemy import ForeignKey

hostServer = os.environ.get('host_serv', 'localhost')
dbServerPort = urllib.parse.quote_plus(str(os.environ.get('db_server_port', '5432')))
dbName = os.environ.get('database_name', 'API-parcial')
dbUserName = urllib.parse.quote_plus(str(os.environ.get('db_username', 'postgres')))
dbPassword = urllib.parse.quote_plus(str(os.environ.get('db_password', 'root1234')))
sslMode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode', 'prefer')))

DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(
    dbUserName,
    dbPassword,
    hostServer,
    dbServerPort,
    dbName,
    sslMode
)

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

usuarios = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("primerApellido", sqlalchemy.String),
    sqlalchemy.Column("segundoApellido", sqlalchemy.String),
    sqlalchemy.Column("direccion", sqlalchemy.String),
    sqlalchemy.Column("municipio", sqlalchemy.String),
    sqlalchemy.Column("codigoPostal", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
    sqlalchemy.Column("observaciones", sqlalchemy.String)
)

libros = sqlalchemy.Table(
    "libros",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("titulo", sqlalchemy.String),
    sqlalchemy.Column("autor", sqlalchemy.Integer, ForeignKey("autores.id")),
    sqlalchemy.Column("materia", sqlalchemy.String),
    sqlalchemy.Column("editorial", sqlalchemy.Integer, ForeignKey("editoriales.id")),
    sqlalchemy.Column("edicion", sqlalchemy.String),
    sqlalchemy.Column("publicacion", sqlalchemy.String),
    sqlalchemy.Column("adquisicion", sqlalchemy.String),
    sqlalchemy.Column("valoracion", sqlalchemy.String),
    sqlalchemy.Column("observaciones", sqlalchemy.String)
)

prestamos = sqlalchemy.Table(
    "prestamos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("usuario_id", sqlalchemy.Integer, ForeignKey("usuarios.id")),
    sqlalchemy.Column("libro_id", sqlalchemy.Integer, ForeignKey("libros.id")),
    sqlalchemy.Column("fechaRetirada", sqlalchemy.String),
    sqlalchemy.Column("devolucion", sqlalchemy.Boolean),
    sqlalchemy.Column("observaciones", sqlalchemy.String),
)

editoriales = sqlalchemy.Table(
    "editoriales",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String),
    sqlalchemy.Column("ciudad", sqlalchemy.String)
)

autores = sqlalchemy.Table(
    "autores",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("apellido", sqlalchemy.String)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    pool_size=3,
    max_overflow=0
)

metadata.create_all(engine)


class UsuarioIn(BaseModel):
    nombre: str
    primerApellido: str
    segundoApellido: str
    direccion: str
    municipio: str
    codigoPostal: str
    telefono: str
    email: str
    observaciones: str


class Usuario(BaseModel):
    id: int
    nombre: str
    primerApellido: str
    segundoApellido: str
    direccion: str
    municipio: str
    codigoPostal: str
    telefono: str
    email: str
    observaciones: str


class LibrosIn(BaseModel):
    titulo: str
    autor: int
    materia: str
    editorial: int
    edicion: str
    publicacion: str
    adquisicion: str
    valoracion:str
    observaciones: str


class Libros(BaseModel):
    id: int
    titulo: str
    autor: str
    materia: str
    editorial: str
    edicion: str
    publicacion: str
    adquisicion: str
    valoracion:str
    observaciones: str


class PrestamosIn(BaseModel):
    usuario_id: int
    libro_id: int
    fechaRetirada: str
    devolucion: bool
    observaciones: str


class Prestamos(BaseModel):
    id: int
    usuario_id: int
    libro_id: int
    fechaRetirada: str
    devolucion: bool
    observaciones: str


class EditorialesIn(BaseModel):
    nombre: str
    telefono: str
    email: str
    ciudad: str


class Editoriales(BaseModel):
    id: int
    nombre: str
    telefono: str
    email: str
    ciudad: str


class AutoresIn(BaseModel):
    nombre: str
    apellido: str


class Autores(BaseModel):
    id: int
    nombre: str
    apellido: str



app = FastAPI(title="API, HM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# USUARIOS

@app.get("/usuarios/", response_model=List[Usuario])
async def read_usuarios(skip: int = 0, take: int = 28):
    query = usuarios.select().offset(skip).limit(take)
    return await database.fetch_all(query)\


@app.get("/usuarios/{id}", response_model=List[Usuario])
async def read_usuarios(id: int):
    query = usuarios.select().where(usuarios.c.id == id)
    return await database.fetch_all(query)


@app.post("/usuarios/", response_model=Usuario)
async def crear_usuarios(user: UsuarioIn):
    query = usuarios.insert().values(
        nombre=user.nombre,
        primerApellido=user.primerApellido,
        segundoApellido=user.segundoApellido,
        direccion=user.direccion,
        municipio=user.municipio,
        codigoPostal=user.codigoPostal,
        telefono=user.telefono,
        email=user.email,
        observaciones=user.observaciones
    )
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.put("/usuarios/{id_usuario}", response_model=Usuario)
async def update_usuarios(id_usuario: int, payload: UsuarioIn):
    query = usuarios.update().where(usuarios.c.id == id_usuario).values(
        nombre=payload.nombre,
        primerApellido=payload.primerApellido,
        segundoApellido=payload.segundoApellido,
        direccion=payload.direccion,
        municipio=payload.municipio,
        codigoPostal=payload.codigoPostal,
        telefono=payload.telefono,
        email=payload.email,
        observaciones=payload.observaciones
    )
    await database.execute(query)
    return {**payload.dict(), "id": id_usuario}


@app.delete("/usuarios/{id_usuarios}")
async def delete_usuarios(id_usuario: int):
    query = usuarios.delete().where(usuarios.c.id == id_usuario)
    await database.execute(query)
    return {"message": "Usuario con el id: {} deleted successfully!".format(id_usuario)}


#lIBROS


@app.get("/libros/", response_model=List[Libros])
async def read_libros(skip: int = 0, take: int = 28):
    query = libros.select().offset(skip).limit(take)
    return await database.fetch_all(query)


@app.get("/libros/{id}", response_model=List[Libros])
async def read_libros(id: int):
    query = libros.select().where(libros.c.id == id)
    return await database.fetch_all(query)


@app.post("/libros/", response_model=Libros)
async def crear_libros(libro: LibrosIn):
    query = libros.insert().values(
        titulo = libro.titulo,
        autor = libro.autor,
        materia = libro.materia,
        editorial = libro.editorial,
        edicion = libro.edicion,
        publicacion = libro.publicacion,
        adquisicion = libro.adquisicion,
        valoracion = libro.valoracion,
        observaciones = libro.observaciones
    )
    last_record_id = await database.execute(query)
    return {**libro.dict(), "id": last_record_id}


@app.put("/libros/{idLibro}", response_model=Libros)
async def update_libros(id_usuario: int, payload: LibrosIn):
    query = libros.update().where(libros.c.id == id_usuario).values(
        titulo=payload.titulo,
        autor=payload.autor,
        materia=payload.materia,
        editorial=payload.editorial,
        edicion=payload.edicion,
        publicacion=payload.publicacion,
        adquisicion=payload.adquisicion,
        valoracion=payload.valoracion,
        observaciones=payload.observaciones
    )
    await database.execute(query)
    return {**payload.dict(), "id": id_usuario}


@app.delete("/libros/{id_libro}")
async def delete_libros(id_libro: int):
    query = libros.delete().where(libros.c.id == id_libro)
    await database.execute(query)
    return {"message": "Libro con el id: {} deleted successfully!".format(id_libro)}



# #PRESTAMOS


@app.get("/prestamos/", response_model=List[Prestamos])
async def read_prestamos(skip: int = 0, take: int = 28):
    query = prestamos.select().offset(skip).limit(take)
    return await database.fetch_all(query)


@app.get("/prestamos/{id}", response_model=List[Prestamos])
async def reat_prestamos(id: int):
    query = prestamos.select().where(prestamos.c.id == id)
    return await database.fetch_all(query)


@app.post("/prestamos/", response_model=Prestamos)
async def crear_prestamos(prestamo: PrestamosIn):
    query = prestamos.insert().values(
        usuario_id = prestamo.usuario_id,
        libro_id = prestamo.libro_id,
        fechaRetirada = prestamo.fechaRetirada,
        devolucion = prestamo.devolucion,
        observaciones = prestamo.observaciones
    )
    last_record_id = await database.execute(query)
    return {**prestamo.dict(), "id": last_record_id}


@app.put("/prestamos/{id_prestamo}", response_model=Prestamos)
async def update_prestamos(id_prestamo: int, payload: PrestamosIn):
    query = prestamos.update().where(prestamos.c.id ==(id_prestamo)).values(
        usuario_id=payload.usuario_id,
        libro_id=payload.libro_id,
        fechaRetirada=payload.fechaRetirada,
        devolucion=payload.devolucion,
        observaciones=payload.observaciones
    )
    await database.execute(query)
    return {**payload.dict(), "id": id_prestamo}


@app.delete("/prestamos/{id_prestamo}")
async def delete_prestamo(id_prestamo: int):
    query = prestamos.delete().where(prestamos.c.id == id_prestamo)
    await database.execute(query)
    return {"message": "Prestamo con el id: {} deleted successfully!".format(id_prestamo)}


#EDITORIAL


@app.get("/editoriales/", response_model=List[Editoriales])
async def read_editorial(skip: int = 0, take: int = 28):
    query = editoriales.select().offset(skip).limit(take)
    return await database.fetch_all(query)


@app.get("/editoriales/{id}", response_model=List[Editoriales])
async def read_editoriales(id: int):
    query = editoriales.select().where(editoriales.c.id == id)
    return await database.fetch_all(query)


@app.post("/editoriales/", response_model=Editoriales)
async def crear_editoriales(editorial: EditorialesIn):
    query = editoriales.insert().values(
        nombre=editorial.nombre,
        telefono=editorial.telefono,
        email=editorial.email,
        ciudad=editorial.ciudad
    )
    last_record_id = await database.execute(query)
    return {**editorial.dict(), "id": last_record_id}


@app.put("/editorial/{id}", response_model=Editoriales)
async def update_editorial(editorial_id: int, payload: EditorialesIn):
    query = editoriales.update().where(editoriales.c.id ==(editorial_id)).values(
        nombre=payload.nombre,
        telefono=payload.telefono,
        email=payload.email,
        ciudad=payload.ciudad
    )
    await database.execute(query)
    return {**payload.dict(), "id": editorial_id}


@app.delete("/editoriales/{id}")
async def delete_editorial(editorial_id: int):
    query = editoriales.delete().where(editoriales.c.id == editorial_id)
    await database.execute(query)
    return {"message": "Editorial con el id: {} deleted successfully!".format(editorial_id)}


#AUTOR

@app.get("/autores/", response_model=List[Autores])
async def read_autores(skip: int = 0, take: int = 28):
    query = autores.select().offset(skip).limit(take)
    return await database.fetch_all(query)


@app.get("/autores/{id}", response_model=List[Autores])
async def read_autores(id: int):
    query = autores.select().where(autores.c.id == id)
    return await database.fetch_all(query)


@app.post("/autores/", response_model=Autores)
async def crear_autores(autor: AutoresIn):
    query = autores.insert().values(
        nombre=autor.nombre,
        apellido=autor.apellido
    )
    last_record_id = await database.execute(query)
    return {**autor.dict(), "id": last_record_id}


@app.put("/autores/{id}", response_model=Autores)
async def update_autores(autor_id: int, payload: AutoresIn):
    query = autores.update().where(autores.c.id ==(autor_id)).values(
        nombre=payload.nombre,
        apellido=payload.apellido
    )
    await database.execute(query)
    return {**payload.dict(), "id": autor_id}


@app.delete("/autores/{id}")
async def delete_autores(autor_id: int):
    query = autores.delete().where(autores.c.id == autor_id)
    await database.execute(query)
    return {"message": "Autor con el id: {} deleted successfully!".format(autor_id)}