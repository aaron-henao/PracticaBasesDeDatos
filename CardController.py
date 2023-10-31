import psycopg2
from datetime import date 
from psycopg2 import sql
from datetime import datetime, timedelta
import SecretConfig


MAX_INTEREST = 100/12

class ExcesiveInterestException( Exception ): 
    """ 
    Custom exception for interest rates above maximun

    Exepcion personalizada para indicar que una tasa de interes supera
    el tope máximo

    """
    def __init__( self, interest_rate ):
        """
    
        """
        super().__init__( f"Invalid interest rate {interest_rate} maximun allowed is {MAX_INTEREST}" )

def ObtenerCursor() :
        """
        Creates the connection to the database and returns a cursor to execute instructions

        Crea la conexion a la base de datos y retorna un cursor para ejecutar instrucciones
        """
        DATABASE = SecretConfig.DATABASE
        USER = SecretConfig.USER
        PASSWORD = SecretConfig.PASSWORD
        HOST = SecretConfig.HOST
        PORT = SecretConfig.PORT
        connection = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        return connection.cursor()
  
        
    
def create_tables():
    """
        Create the tables in the database
            
        Crea las tablas en la base de datos
    """
    try:
         cursor = ObtenerCursor()
         create_credit_card_table = sql.SQL('''CREATE TABLE IF NOT EXISTS credit_card (
             card_number VARCHAR(16),
             owner_id VARCHAR(10),
             owner_name VARCHAR(255),
              bank_name VARCHAR(255),
              due_date DATE,
              franchise VARCHAR(255),
              payment_day INTEGER,
              monthly_fee NUMERIC(10, 2),
              interest_rate NUMERIC(5, 2)
            )''')

         create_payment_plan = sql.SQL('''create table payment_plan(
            card_number varchar(20) not null,
            purchase_date date not null,
            purchase_amount float not null,
            payment_day int not null,
            payment_amount float not null,
            interest_amount float not null,
            capital_amount float not null,
            balance float not null

            );''')
         # Ejecutar las consultas SQL - Executing SQL queries
         cursor.execute(create_credit_card_table)
         cursor.execute(create_payment_plan)

         cursor.connection.commit()
         cursor.close()
         cursor.connection.close()
         return "Tablas creadas exitosamente - Successfully created tables"
    except Exception as e:
         return str(e)
    
   

def register_credit_card(card):
    """
    The card is registered in the database

    Se realiza el registro de la tarjeta en la base de datos
    """
    try:
        cursor = ObtenerCursor()

        # Obtener la fecha de vencimiento como una cadena en el formato "31/12/2027"
        #  Get the expiration date as a string in the format "12/31/2027"
        due_date_str = card.due_date
        due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()  # Convertir la cadena a fecha

        # Verificar si la fecha de vencimiento es menor que la fecha actual
        # Check if the due date is less than the current date
        current_date = datetime.now().date()
        if due_date < current_date:
            return "No se permite guardar la tarjeta porque está vencida"

        # Continuar con la inserción de la tarjeta si no está vencida
        # Continue with the insertion of the card if it is not expired
        insert_query = sql.SQL('''INSERT INTO credit_card (card_number, owner_id, owner_name, bank_name, due_date, franchise, payment_day, monthly_fee, interest_rate)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''')
        cursor.execute(insert_query, (
            card.card_number, card.owner_id, card.owner_name, card.bank_name, due_date, card.franchise,
            card.payment_day, card.monthly_fee, card.interest_rate))
        cursor.connection.commit()
        return "Tarjeta guardada exitosamente"
    except psycopg2.IntegrityError:
        return "No permite guardar la tarjeta, porque ya existe"
    except Exception as e:
        return str(e)

def checkInterest(interest_rate):
        """ 
        Verify that the interest rate does not exceed the maximum allowed

        Verifica que la tasa de interés no supere la maxima permitida
        """
        if interest_rate > MAX_INTEREST :
            """ 
            If interest rate is above MAX_INTEREST_RATE raises ExcesiveInterestException
            Si la tasa es mayor que MAX_INTEREST_RATE, arroja una excepcion ExcesiveInterestException """
            raise ExcesiveInterestException( interest_rate )

def calculate_fee_payment(purchase_amount : float,interest_rate : float, monthly_payments : int):

        checkInterest(interest_rate)

        if monthly_payments == 1 :
            """ 
            If periods equals one, no interests are calculated

            Cuando el plazo sea una sola cuota, no se aplican intereses 
            """
            return purchase_amount

        """ La tasa de interés está expresada como un entero entre 1 y 100 """
        i =  interest_rate / 100
    
        if interest_rate == 0:
            """ 
            Cuando la tasa sea cero, la cuota es la compra dividida las cuotas
            para evitar error de division por cero 
            """
            return purchase_amount / monthly_payments  # Divide el monto por la cantidad de cuotas
                                     # Retorna el interes a pagar
        else:         
            return (purchase_amount * i) / (1 - (1 + i) ** (-monthly_payments))

         

def calculate_interest(monthly_payment: float, num_installments: int, purchase_amount: float, interest_rate):
    """
        Calculate interest

        Calcula el interés
    """
    
    
    if num_installments == 1:
        return 0  # Si hay una sola cuota, no hay intereses - If there is only one installment, there is no interest

    total_interest = (monthly_payment * num_installments) - purchase_amount
    return total_interest
     


def calculate_payment(purchase_amount: float, card: dict, num_installments: int):
    """
        Calculate the payment of the total interest and the fee for each purchase

        Calcula el pago del total de intereses y la cuota para cada compra
    """
    
    
    try:
        if purchase_amount <= 0:
            raise Exception("Error: El Monto debe ser superior a cero")

        interest_rate = card.get("interest_rate")

        if interest_rate is None:
            raise Exception("Error: La tarjeta indicada no existe")

        checkInterest(interest_rate)

        if num_installments <= 0:
            raise Exception("Error: El numero de cuotas debe ser mayor a cero")

        if num_installments == 1:
            monthly_payment = purchase_amount
            total_interest = 0
        else:
            i = interest_rate / 100

            if interest_rate == 0:
                monthly_payment = purchase_amount / num_installments
            else:
                monthly_payment = (purchase_amount * i) / (1 - (1 + i) ** (-num_installments))

            total_interest = (monthly_payment * num_installments) - purchase_amount

        return f"Total Intereses: {total_interest:.2f} - Cuota: {monthly_payment:.4f}"

    except ExcesiveInterestException as e:
        return f"Error: {str(e)}", None
    except Exception as e:
        return str(e) 


def make_purchase(purchase_amount: float, interest_rate: float, monthly_payment: float):
    """
        Shows the number of months for scheduled savings
    
        Muestra el número de meses para el ahorro programado
    """
    try:
        # Validaciones
        if purchase_amount <= 0:
            return "Error: El Monto debe ser superior a cero"
        if interest_rate <= 0:
            return "Error: La tasa de interés debe ser mayor a cero"
        if monthly_payment <= 0:
            return "Error: El monto de ahorro mensual debe ser mayor a cero"
        
        interest_rate = interest_rate/100
        initial_amount = 0
        num_months= 0

        while initial_amount<purchase_amount:
             if num_months == 0:
                initial_amount += monthly_payment
                num_months += 1
             else:
                 initial_amount += monthly_payment
                 initial_amount += initial_amount * interest_rate
                 num_months += 1
        num_months += 1

        if monthly_payment >= purchase_amount:
             num_months = num_months -1
             return f"Número de meses ahorrando: {num_months}"
        
    
        return f"Número de meses ahorrando: {num_months}"

    except Exception as e:
        return str(e)

def calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date):
    try:
        cursor = ObtenerCursor()

        monthly_payment = calculate_fee_payment(purchase_amount, interest_rate, num_installments)

        # Calcula las fechas de pago
        payment_dates = []
        payment_date = datetime.strptime(purchase_date, '%Y-%m-%d')
        for _ in range(num_installments):
            payment_dates.append(payment_date.strftime('%Y-%m-%d'))
            payment_date += timedelta(months=1)

        # Calcula los montos de interés y capital
        balance = purchase_amount
        """
        interest_amounts = []
        capital_amounts = []
        for _ in range(num_installments):
            interest_amount = balance * (interest_rate / 100 / 12)
            capital_amount = monthly_payment - interest_amount
            interest_amounts.append(interest_amount)
            capital_amounts.append(capital_amount)
            balance -= capital_amount
            total_intereses = sum(interest_amounts)
            total_abonos = sum(capital_amounts)
        payment_amount = monthly_payment
        

        # Inserta la información en la tabla payment_plan
        for i in range(num_installments):
            insert_query = sql.SQL("INSERT INTO payment_plan (card_number, purchase_date, purchase_amount, payment_day, payment_amount, interest_amount, capital_amount, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"),
                                   
            cursor.execute(insert_query, (card_number, purchase_date, purchase_amount, payment_day, payment_amount, interest_amounts[i], capital_amounts[i], balance))
            cursor.connection.commit()"""
        total_abonos = 0
        total_intereses = 0
        for i in range(num_installments):
            interest_amount = balance * (interest_rate / 100 / 12)
            capital_amount = monthly_payment - interest_amount
            balance -= capital_amount
            total_abonos += capital_amount
            total_intereses += interest_amount
        


            # Insertar cada cuota en una fila
            insert_query = "INSERT INTO payment_plan (card_number, purchase_date, purchase_amount, payment_day, payment_amount, interest_amount, capital_amount, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data = (card_number, purchase_date, purchase_amount, payment_dates[i], monthly_payment, interest_amount, capital_amount, balance)
            cursor.execute(insert_query, data)
            cursor.connection.commit()

        cursor.close()
        cursor.connection.close()
        return f"Cuota mensual = {monthly_payment}, Total Abonos = {total_abonos}, Total intereses = {total_intereses}"

    except Exception as e:
        return "No se pudo guardar el plan de amortización"

def insert_amortization_plan():
    try:
        cursor = ObtenerCursor
        card = calculate_amortization_plan
    except Exception as e:
        return "No se pudo guardar el plan de amortización"   
    
def get_monthly_payments_report(card_number: int, start_date: date , end_date: date):
        """
            Gets the payment report according to the indicated date
        
            Obtiene el reporte de pagos según la fecha indicada
        """
        try:
            cursor = ObtenerCursor()

            cursor.execute(
                "SELECT interest_rate FROM credit_card WHERE card_number = %s", (card_number,))
            row = cursor.fetchone()
            if row is None:
                return "La tarjeta indicada no existe"
            
            query = sql.SQL('''SELECT card_number, purchase_date, 
                               FROM amortization_plan
                               WHERE card_number = %s AND installment_due_date >= %s AND installment_due_date <= %s
                               ORDER BY installment_due_date''')
            cursor.execute(query, (card_number, start_date, end_date))
            rows = cursor.fetchall()
            
        
        except Exception as e:
            return ""
        try:
            cursor = ObtenerCursor()
            # Verificar si la tarjeta existe - Check if the card exists
            cursor.execute(
                "SELECT interest_rate FROM credit_card WHERE card_number = %s", (card_number,))
            row = cursor.fetchone()
            if row is None:
                return "La tarjeta indicada no existe"

            # Consultar las cuotas en el rango de fechas - See odds in the date range
            query = sql.SQL('''SELECT installment_due_date, installment_amount
                               FROM amortization_plan
                               WHERE card_number = %s AND installment_due_date >= %s AND installment_due_date <= %s
                               ORDER BY installment_due_date''')
            cursor.execute(query, (card_number, start_date, end_date))
            rows = cursor.fetchall()

            # Calcular el total de cuotas mensuales - Calculate total monthly installments
            total_monthly_payments = 0.0
            for row in rows:
                total_monthly_payments += row[1]

            return f"Total de cuotas mensuales en el rango: {total_monthly_payments:.2f}"

        except Exception as e:
            return str(e)

def close_connection():
        cursor = ObtenerCursor()
        cursor.close()
        cursor.connection.close()

if __name__ == "__main__":
    result = create_tables()
    print(result)