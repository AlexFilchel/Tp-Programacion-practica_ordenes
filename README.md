# TP Programacion - API de Productos y Ordenes

## Descripcion general

Este proyecto implementa una **API REST** para gestionar **productos** y **ordenes de compra**.
Esta construida con **FastAPI**, usa **SQLModel/SQLAlchemy** para persistencia y guarda los datos en **SQLite** (`database.db`).

La idea central del sistema es simple:

1. Se crean productos.
2. Se crea una orden enviando un email de usuario y una lista de items.
3. El sistema busca cada producto, calcula subtotales y el total final.
4. Guarda la orden y sus items dentro de una transaccion.
5. Permite consultar una orden puntual o listar ordenes paginadas.

---

## Stack tecnologico

- **FastAPI**: capa HTTP y definicion de endpoints.
- **SQLModel / SQLAlchemy**: modelos de base de datos y sesiones.
- **SQLite**: base embebida en el archivo `database.db`.
- **Pydantic**: validacion y serializacion de DTOs.
- **Uvicorn**: servidor ASGI para ejecutar la API.

---

## Estructura del proyecto

```text
app/
|- db.py                  # engine, sesion y creacion de tablas
|- main.py                # arranque de FastAPI y registro de routers
|- models/
|  |- Producto.py         # tabla de productos
|  |- Orden.py            # tabla de ordenes
|  `- OrderItem.py        # tabla intermedia de items de orden
|- routers/
|  |- productos.py        # endpoint para crear productos
|  `- ordenes.py          # endpoints para crear y consultar ordenes
|- schemas/
|  |- ProductoDTO.py      # DTOs de entrada/salida de productos
|  `- OrdenDTO.py         # DTOs de entrada/salida de ordenes
|- services/
|  `- orden_service.py    # logica de negocio de ordenes
`- uow/
   `- unit_of_work.py     # manejo transaccional con patron Unit of Work
```

---

## Como arranca el sistema

El punto de entrada es `app/main.py`.

### Que hace al arrancar

- Crea una app de FastAPI.
- Ejecuta `crear_base_de_datos()` dentro del `lifespan`.
- Esa funcion corre `SQLModel.metadata.create_all(engine)`.
- Si las tablas no existen, las crea automaticamente en `database.db`.
- Registra los routers de:
  - `/productos`
  - `/ordenes`

### Endpoint base

```http
GET /
```

Respuesta:

```json
{ "message": "API funcionando" }
```

---

## Modelo de datos

El sistema tiene **3 tablas**.

### 1. `producto`
Representa los productos disponibles para comprar.

Campos:
- `id`
- `name`
- `price`

### 2. `orden`
Representa la cabecera de una compra.

Campos:
- `id`
- `user_email`
- `total_amount`
- `created_at`

### 3. `orderitem`
Representa cada linea de detalle de una orden.

Campos:
- `id`
- `order_id`
- `product_id`
- `quantity`
- `unit_price`

### Relacion entre tablas

- Una **orden** tiene muchos **items**.
- Cada **item** apunta a un **producto**.
- `orderitem` funciona como tabla de detalle entre `orden` y `producto`.

---

## Arquitectura y responsabilidades


### `routers/`
Reciben requests HTTP, validan parametros de entrada y delegan.

- `productos.py`: crea productos directamente con una sesion inyectada.
- `ordenes.py`: delega la logica a `OrdenService`.

### `schemas/`
Definen los contratos de entrada y salida.

Ejemplos:
- `ProductoCreate`
- `ProductoRead`
- `OrdenCreate`
- `OrdenRead`
- `OrdenDetalleRead`
- `OrdenPaginadaRead`

Esto evita exponer directamente los modelos internos como contrato de API.

### `models/`
Representan las tablas reales de base de datos.

### `services/`
Contienen la logica de negocio.

`OrdenService` resuelve:
- creacion de ordenes
- calculo del total
- verificacion de existencia de productos
- armado de respuestas detalladas
- listado paginado

### `uow/`
Implementa el patron **Unit of Work**.

Su trabajo es manejar una sesion transaccional:
- abre la sesion al entrar
- hace rollback si ocurre una excepcion
- cierra la sesion al salir
- expone `commit()` y `rollback()`


---

## Flujo funcional del sistema

## 1. Crear un producto

### Endpoint

```http
POST /productos
```

### Body

```json
{
  "name": "Teclado",
  "price": 15000
}
```

### Que ocurre internamente

1. El router recibe `ProductoCreate`.
2. FastAPI inyecta una sesion desde `get_session()`.
3. Se instancia `Producto`.
4. Se guarda con `session.add()`.
5. Se hace `commit()`.
6. Se hace `refresh()` para recuperar el `id` generado.
7. Se devuelve `ProductoRead`.

---

## 2. Crear una orden

### Endpoint

```http
POST /ordenes
```

### Body

```json
{
  "user_email": "cliente@mail.com",
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 2, "quantity": 1 }
  ]
}
```

### Que ocurre internamente

1. El router recibe `OrdenCreate`.
2. Crea una instancia de `OrdenService`.
3. El servicio abre un `UnitOfWork`.
4. Inserta una `Orden` con `total_amount = 0`.
5. Ejecuta `flush()` para obtener el `id` de la orden antes del `commit`.
6. Recorre los items recibidos.
7. Busca cada producto por `product_id`.
8. Si un producto no existe, lanza `HTTPException(404)`.
9. Calcula `subtotal = producto.price * quantity`.
10. Acumula el total general.
11. Crea un `OrderItem` por cada linea.
12. Actualiza `orden.total_amount` con el total final.
13. Hace `commit()`.
14. Refresca la orden y devuelve una respuesta resumida.

### Por que usa una transaccion

Porque crear una orden implica varias escrituras:
- una fila en `orden`
- varias filas en `orderitem`

Si algo falla en el medio, el rollback evita dejar datos inconsistentes.

---

## 3. Obtener una orden por ID

### Endpoint

```http
GET /ordenes/{order_id}
```

### Que ocurre internamente

1. El router delega a `OrdenService`.
2. El servicio busca la orden por ID.
3. Si no existe, responde `404`.
4. Hace una consulta con `join` entre `OrderItem` y `Producto`.
5. Construye manualmente una respuesta detallada.
6. Devuelve:
   - datos de la orden
   - lista de items
   - producto embebido en cada item

### Respuesta esperada

```json
{
  "id": 1,
  "user_email": "cliente@mail.com",
  "total_amount": 35000,
  "items": [
    {
      "product": {
        "id": 1,
        "name": "Teclado",
        "price": 15000
      },
      "quantity": 2,
      "unit_price": 15000
    }
  ]
}
```

---

## 4. Listar ordenes paginadas

### Endpoint

```http
GET /ordenes?offset=0&limit=10
```

### Que devuelve y como funciona

1. Cuenta el total de ordenes existentes.
2. Recupera una ventana usando `offset` y `limit`.
3. Devuelve una respuesta con:
   - `total`: cantidad total de ordenes
   - `data`: lista resumida de ordenes

### Respuesta esperada

```json
{
  "total": 25,
  "data": [
    {
      "id": 1,
      "user_email": "cliente@mail.com",
      "total_amount": 35000
    }
  ]
}
```

---

## Contratos de API

### Productos

#### Crear producto
- **POST** `/productos`

Solicitud:

```json
{
  "name": "Mouse",
  "price": 5000
}
```

Respuesta:

```json
{
  "id": 1,
  "name": "Mouse",
  "price": 5000
}
```

### Ordenes

#### Crear orden
- **POST** `/ordenes`

#### Obtener orden
- **GET** `/ordenes/{order_id}`

#### Listar ordenes
- **GET** `/ordenes?offset=0&limit=10`

---

## Validaciones verificadas en el codigo

- `quantity` debe ser mayor que 0 (`Field(gt=0)`).
- `offset` debe ser mayor o igual a 0.
- `limit` debe ser mayor que 0.
- Si un producto no existe al crear una orden, la API responde `404` con:

```json
{ "detail": "Producto no encontrado" }
```

- Si una orden no existe al consultarla, la API responde `404` con:

```json
{ "detail": "Orden no encontrada" }
```

---

## Como ejecutar el proyecto

### 1. Activar el entorno virtual

En PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 3. Levantar la API

```powershell
uvicorn app.main:app --reload
```

### 4. Probar documentacion automatica

FastAPI expone por defecto:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---