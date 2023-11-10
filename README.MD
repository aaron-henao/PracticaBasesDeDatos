AARON DAVID GIRALDO HENAO


Crear una aplicación web que permita al usuario:

1. Registrar una tarjeta de crédito
2. Simular una compra con su tarjeta
3. Sugerir al usuario un plan de ahorro programado que le muestre cuántos meses debe ahorrar en vez utilizar su tarjeta para una compra.
4. Registrar una compra con la tarjeta de crédito y guardar el plan de amortización en una tabla de la base de datos.
5. Permitir al usuario ver un informe del total de la suma de las cuotas mensuales que debe pagar por sus compras dadas las fechas.
6. Permitir al usuario borrar la tarjeta de crédito del sistema.

Para instalar:

1. Insertar datos de la base de datos en el archivo SecretConfig-sample.py y renombrarlo como SecretConfig.py
2. Instalar dateutil 'pip install python-dateutil'
3. Instalar psycopg2 'pip install psycopg2'
4. Ejecutar CardController para crear las tablas credit_card y payment_plan en su base de datos

Para ejecutar:

1. Instalar Flask 'pip install Flask'
2. Ejecutar archivo app.py
3. Accede a la app desde tu navegador: 'http://localhost:5000' o con la dirección de tu servidor local.
4. Accede al menú principal de la app añadiendo a la dirección de tu servidor local '/'
