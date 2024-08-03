import os
import uuid
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

# ---------------------------------------------------
NOMBRE, PRECIO, CANTIDAD = range(3)
NOMBRE_ACTUALIZAR, PRECIO_ACTUALIZAR, CANTIDAD_ACTUALIZAR = range(3)
ELIMINAR_NOMBRE = ''

### * Iniciar Conversacion
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    """Selecciona una opcion: 
      /insertar para agregar un nuevo artículo.
      /actualizar para actualizar un artículo.
      /eliminar para eliminar un artículo.

      /producto_cerca_acabarse para ver los articulos cerca de acabarse.
      /costo_total para ver precio por la cantidad y sumando todos los productos.
      /listar Para ver todos los articulos.
    """)

### * Insertar Producto
async def insertar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text('Por favor, envía el nombre del artículo.')
  return NOMBRE

async def obtener_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data['nombre'] = update.message.text
  await update.message.reply_text('Ahora envía el precio del artículo.')
  return PRECIO

async def obtener_precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data['precio'] = update.message.text
  await update.message.reply_text('Por último, envía la cantidad del artículo.')
  return CANTIDAD

async def obtener_cantidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data['cantidad'] = update.message.text
  nombre = context.user_data['nombre']
  precio = context.user_data['precio']
  cantidad = context.user_data['cantidad']

  await update.message.reply_text(
      f'Artículo: {nombre}\nPrecio: {precio}\nCantidad: {cantidad}\n¡Artículo insertado con éxito!'
  )

  # Guardar en un archivo .txt separado por pipes
  with open('articulos.txt', 'a') as file:
    file.write(f'\n{nombre}|{precio}|{cantidad}')
  
  return ConversationHandler.END

### * Listar Productos
async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # Leer todos los artículos del archivo
  with open('articulos.txt', 'r') as file:
    lineas = file.readlines()
  
  list_articulos = 'Nombre --- Precio --- Cantidad\n'
  for linea in lineas:
    nombre, precio, cantidad = linea.strip().split('|')
    list_articulos += f'{nombre} --- ${precio} --- {cantidad}\n'
  
  await update.message.reply_text(f'Articulos. \n{list_articulos}')

### * Actualizar Producto
async def actualizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # Leer todos los artículos del archivo
  with open('articulos.txt', 'r') as file:
    lineas = file.readlines()
  
  list_nombres = ''
  for linea in lineas:
    nombre, precio, cantidad = linea.strip().split('|')
    list_nombres += f'➡️ {nombre}\n'
  
  await update.message.reply_text(f'Por favor, envía el nombre del artículo que deseas actualizar. \n{list_nombres}')
  return NOMBRE_ACTUALIZAR

async def obtener_nombre_actualizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data['nombre_actualizar'] = update.message.text
  await update.message.reply_text('Ahora envía el nuevo precio del artículo.')
  return PRECIO_ACTUALIZAR

async def obtener_precio_actualizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data['precio_actualizar'] = update.message.text
  await update.message.reply_text('Por último, envía la nueva cantidad del artículo.')
  return CANTIDAD_ACTUALIZAR

async def obtener_cantidad_actualizar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data['cantidad_actualizar'] = update.message.text
  nombre_actualizar = context.user_data['nombre_actualizar']
  nuevo_precio = context.user_data['precio_actualizar']
  nueva_cantidad = context.user_data['cantidad_actualizar']

  # Leer todos los artículos del archivo
  with open('articulos.txt', 'r') as file:
      lineas = file.readlines()

  # Escribir los artículos actualizados en el archivo
  with open('articulos.txt', 'w') as file:
      for linea in lineas:
          nombre, precio, cantidad = linea.strip().split('|')
          if nombre == nombre_actualizar:
              file.write(f'{nombre}|{nuevo_precio}|{nueva_cantidad}')
          else:
              file.write(linea)

  await update.message.reply_text(
      f'Artículo actualizado: {nombre_actualizar}\nNuevo precio: {nuevo_precio}\nNueva cantidad: {nueva_cantidad}\n¡Artículo actualizado con éxito!'
  )

  return ConversationHandler.END

### * Eliminar Producto
async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # Leer todos los artículos del archivo
  with open('articulos.txt', 'r') as file:
    lineas = file.readlines()
  
  list_nombres = ''
  for linea in lineas:
    nombre, precio, cantidad = linea.strip().split('|')
    list_nombres += f'➡️ {nombre}\n'

  await update.message.reply_text(f'Por favor, envía el nombre del artículo que deseas eliminar. \n{list_nombres}')
  return ELIMINAR_NOMBRE

async def obtener_nombre_eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  nombre_eliminar = update.message.text

  # Leer todos los artículos del archivo
  with open('articulos.txt', 'r') as file:
      lineas = file.readlines()

  # Escribir los artículos en el archivo, omitiendo el que se va a eliminar
  with open('articulos.txt', 'w') as file:
      articulo_encontrado = False
      for linea in lineas:
          nombre, precio, cantidad = linea.strip().split('|')
          if nombre == nombre_eliminar:
              articulo_encontrado = True
          else:
              file.write(linea)
  
  if articulo_encontrado:
      await update.message.reply_text(f'¡Artículo "{nombre_eliminar}" eliminado con éxito!')
  else:
      await update.message.reply_text(f'Artículo "{nombre_eliminar}" no encontrado.')

  return ConversationHandler.END

### * Función para encontrar el producto más cercano a acabarse
async def producto_mas_cerca_de_acabarse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('articulos.txt', 'r') as file:
            lineas = file.readlines()

        min_producto = None
        min_cantidad = float('inf')

        for linea in lineas:
            nombre, precio, cantidad = linea.strip().split('|')
            cantidad = int(cantidad)
            if cantidad < min_cantidad:
                min_cantidad = cantidad
                min_producto = (nombre, cantidad)

        if min_producto:
            await update.message.reply_text(f"El producto más cercano a acabarse es '{min_producto[0]}' con una cantidad de {min_producto[1]}.")
        else:
            await update.message.reply_text("No hay productos en el inventario.")
    except FileNotFoundError:
        await update.message.reply_text("El archivo de artículos no existe.")

### * Función para calcular el costo total del inventario
async def costo_total_inventario(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    with open('articulos.txt', 'r') as file:
      lineas = file.readlines()

    costo_total = 0.0

    for linea in lineas:
      nombre, precio, cantidad = linea.strip().split('|')
      precio = float(precio)
      cantidad = int(cantidad)
      costo_total += precio * cantidad

    await update.message.reply_text(f"El costo total del inventario es: ${costo_total:.2f}")
  except FileNotFoundError:
    await update.message.reply_text("El archivo de artículos no existe.")

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text('Operación cancelada.')
  return ConversationHandler.END


if __name__ == "__main__":
  app = Application.builder()\
    .token(TOKEN).build()

  conv_handler_insert = ConversationHandler(
    entry_points=[CommandHandler('insertar', insertar)],
    states={
      NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_nombre)],
      PRECIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_precio)],
      CANTIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_cantidad)]
    },
    fallbacks=[CommandHandler('cancelar', cancelar)],
  )

  conv_handler_update = ConversationHandler(
    entry_points=[CommandHandler('actualizar', actualizar)],
    states={
      NOMBRE_ACTUALIZAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_nombre_actualizar)],
      PRECIO_ACTUALIZAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_precio_actualizar)],
      CANTIDAD_ACTUALIZAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_cantidad_actualizar)]
    },
    fallbacks=[CommandHandler('cancelar', cancelar)],
  )

  conv_handler_eliminar = ConversationHandler(
    entry_points=[CommandHandler('eliminar', eliminar)],
    states={
      ELIMINAR_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, obtener_nombre_eliminar)],
    },
    fallbacks=[CommandHandler('cancelar', cancelar)],
  )

  app.add_handler(CommandHandler('start', start))
  app.add_handler(CommandHandler('listar', listar))
  app.add_handler(conv_handler_insert)
  app.add_handler(conv_handler_update)
  app.add_handler(conv_handler_eliminar)
  app.add_handler(CommandHandler('producto_cerca_acabarse', producto_mas_cerca_de_acabarse))
  app.add_handler(CommandHandler('costo_total', costo_total_inventario))

  app.run_polling(poll_interval=1)
