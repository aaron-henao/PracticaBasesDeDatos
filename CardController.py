import psycopg2
from datetime import date 
from psycopg2 import sql
from datetime import datetime
import SecretConfig
from dateutil.relativedelta import relativedelta
from Card import CreditCard


MAX_INTEREST = 100/12

class Errors (Exception):
    pass

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

    try:
         cursor = ObtenerCursor()
         create_credit_card_table = sql.SQL(f"""create table  IF NOT EXISTS credit_card(
        card_number VARCHAR(16),
        owner_id VARCHAR(10),
        owner_name VARCHAR(255),
        bank_name VARCHAR(255),
        due_date DATE,
        franchise VARCHAR(255),
        payment_day INTEGER,
        monthly_fee FLOAT,
         interest_rate FLOAT)""")

         create_payment_plan = sql.SQL("""create table payment_plan(
            card_number varchar(20) not null,
            purchase_date date not null,
            payment_date date not null,
            purchase_amount float not null,
            payment_amount float not null,
            interest_amount float not null,
            capital_amount float not null,
            balance float not null) 
                                        """)
        
    
def create_tables():
    """
        Create the tables in the database
            
        Crea las tablas en la base de datos
    """
    sql = ""
    with open("sql/create-tables.sql","r") as f:
        sql = f.read()

    cursor = ObtenerCursor()


    try:
         cursor.execute( sql )
         cursor.connection.commit()
         return "Tablas creadas correctamente"

    except:
        cursor.connection.rollback
        return "Las tablas ya existen"

# Aplicación web
def insert_card(card: CreditCard):

    cursor = ObtenerCursor()
    cursor.execute(f"""
        insert into credit_card (
                    card_number, owner_id, owner_name, bank_name, due_date, franchise, payment_day, monthly_fee, interest_rate
        )
        values
        (
            '{card.card_number}', '{card.owner_id}', '{card.owner_name}', '{card.bank_name}', TO_DATE('{card.due_date}', 'YYYY-MM-DD'), '{card.franchise}',
            '{card.payment_day}', '{card.monthly_fee}', '{card.interest_rate}'
        ); 
                    """)
    cursor.connection.commit()


def delete_card(card_number):
    
    cursor = ObtenerCursor()
    cursor.execute(f"""
            delete from credit_card where card_number = '{card_number}'
        """)
    cursor.execute(f"""
            delete from payment_plan where card_number = '{card_number}'
        """)
    cursor.connection.commit()
    cursor.close()


#Caso de prueba                
def register_credit_card(card: CreditCard):
    """
    The card is registered in the database

    Se realiza el registro de la tarjeta en la base de datos
    """
    try: 
        cursor = ObtenerCursor()

        # Obtener la fecha de vencimiento como una cadena en el formato "31/12/2027"
        #  Get the expiration date as a string in the format "12/31/2027"
        due_date_str = card.due_date
        card.due_date = datetime.strptime(due_date_str, "%d/%m/%Y").date()  # Convertir la cadena a fecha

        # Verificar si la fecha de vencimiento es menor que la fecha actual
        # Check if the due date is less than the current date
        current_date = datetime.now().date()
        if card.due_date < current_date:
            raise ValueError("No se permite guardar la tarjeta porque está vencida")
        

        cursor.execute(f"""
        insert into credit_card (
                card_number, owner_id, owner_name, bank_name, due_date, franchise, payment_day, monthly_fee, interest_rate
        )
        values
        (
            '{card.card_number}', '{card.owner_id}', '{card.owner_name}', '{card.bank_name}', TO_DATE('{card.due_date}', 'YYYY-MM-DD'), '{card.franchise}',
            '{card.payment_day}', '{card.monthly_fee}', '{card.interest_rate}'
        );
            
                       """)
        cursor.connection.commit()
        raise ValueError("Tarjeta guardada exitosamente")
    
    except psycopg2.IntegrityError:
        raise ValueError("No permite guardar la tarjeta, porque ya existe")
    except:
        cursor.connection.rollback


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

def calculate_fee_payment(purchase_amount : float,interest_rate : float, monthly_payments):

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
     


def calculate_payment(purchase_amount: float, interest_rate:float , num_installments: int):
    """
        Calculate the payment of the total interest and the fee for each purchase

        Calcula el pago del total de intereses y la cuota para cada compra
    """
    
    try:
        
        if purchase_amount <= 0:
            raise Exception("Error: El Monto debe ser superior a cero")

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

        total_interest = round(total_interest, 2)
        monthly_payment = round(monthly_payment, 4)

        return total_interest, monthly_payment
        

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
             return num_months
        
    
        return num_months

    except Exception as e:
        return str(e)
    
# Aplicación web
def calculate_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date):
    plan= []
    monthly_payment = calculate_fee_payment(purchase_amount, interest_rate, num_installments)

    if num_installments > 1:
            
            # Calcula las fechas de pago
        payment_dates = []
        payment_date = datetime.strptime(purchase_date, '%Y-%m-%d')
            
        for _ in range(num_installments):
             payment_dates.append(payment_date.strftime('%Y-%m-%d'))
             payment_date += relativedelta(months=1)

            # Calcula los montos de interés y capital
        balance = purchase_amount
        
            
        for i in range(num_installments):
            monthly_interest_rate = interest_rate / 100 / 12
            interest_amount = balance * monthly_interest_rate
            capital_amount = monthly_payment - interest_amount
            balance -= capital_amount
            
            plan.append({
                    'card_number': card_number,
                    'purchase_date': purchase_date,
                    'payment_date': payment_dates[i],
                    'purchase_amount': purchase_amount,
                    'payment_amount': monthly_payment,
                    'interest_amount': interest_amount,
                    'capital_amount': capital_amount,
                    'balance': balance
                })
    return plan

# Aplicación web
def insert_plan(plan):
    try:
        cursor = ObtenerCursor()

        for installment in plan:
            insert_query = """
                INSERT INTO payment_plan (card_number, purchase_date, payment_date, purchase_amount, payment_amount, interest_amount, capital_amount, balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                installment['card_number'], installment['purchase_date'], installment['payment_date'],
                installment['purchase_amount'], installment['payment_amount'], installment['interest_amount'],
                installment['capital_amount'], installment['balance']
                ))
            
        cursor.connection.commit()
        cursor.close()

        return "Plan de amortización almacenado en la base de datos correctamente"
    
    except Exception as e:

        return f"No se pudo almacenar el plan de amortización en la base de datos: {str(e)}"

            
#Caso de prueba 
def calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date, payment_day):
    try:

        cursor = ObtenerCursor()
        monthly_payment = calculate_fee_payment(purchase_amount, interest_rate, num_installments)

        if num_installments > 1:
            
            # Calcula las fechas de pago
            payment_dates = []
            payment_date = datetime.strptime(purchase_date, '%Y-%m-%d')
            
            for _ in range(num_installments):
                payment_dates.append(payment_date.strftime('%Y-%m-%d'))
                payment_date += relativedelta(months=1)

            # Calcula los montos de interés y capital
            balance = purchase_amount
            total_abonos = 0
            total_intereses = 0
            
            for i in range(num_installments):
                interest_amount = balance * (interest_rate / 100 / 12)
                capital_amount = monthly_payment - interest_amount
                balance -= capital_amount
                total_abonos += capital_amount
                total_intereses += interest_amount

                insert_query = sql.SQL ("""
                    INSERT INTO payment_plan (card_number, purchase_date, payment_date, purchase_amount, payment_amount, interest_amount, capital_amount, balance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """)
                
                cursor.execute(insert_query, (card_number, purchase_date, payment_dates[i], purchase_amount, monthly_payment, interest_amount, capital_amount, balance))
                cursor.connection.commit()

            cursor.close()
            return f"Cuota mensual = {monthly_payment}, Total Abonos = {total_abonos}, Total intereses = {total_intereses}"
        else:

            return f"Cuota mensual = {monthly_payment}, Total Abonos = {purchase_amount}, Total intereses = {total_intereses}"

    except Exception as e:
        return "No se pudo guardar el plan de amortización"

#Caso de prueba    
def get_monthly_payments_report(start_date: date, end_date: date):
    try:
        cursor = ObtenerCursor()
        
        query = sql.SQL('''SELECT payment_plan.payment_amount
                           FROM payment_plan
                           INNER JOIN credit_card ON payment_plan.card_number = credit_card.card_number
                           WHERE credit_card.owner_id = '1010123456' AND payment_plan.payment_date >= %s and payment_plan.payment_date <= %s''')
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()

        total_monthly_payments = sum(row[0] for row in rows)  # Suma de los montos de cuotas mensuales

        return f"Total: {total_monthly_payments:.2f}"
    
    except Exception as e:
        return str(e)

# Aplicación web
def get_monthly_payments_reports(start_date: date, end_date: date, owner_id: str):
    try:
        cursor = ObtenerCursor()
        
        query = sql.SQL('''
            SELECT payment_plan.payment_amount
            FROM payment_plan
            INNER JOIN credit_card ON payment_plan.card_number = credit_card.card_number
            WHERE credit_card.owner_id = %s 
            AND payment_plan.payment_date >= %s 
            AND payment_plan.payment_date <= %s
        ''')
        
        cursor.execute(query, (owner_id, start_date, end_date))
        rows = cursor.fetchall()

        total_monthly_payments = sum(row[0] for row in rows)  # Suma de los montos de cuotas mensuales

        return f"Total: {total_monthly_payments:.2f}"
    
    except Exception as e:
        return str(e)

def close_connection():
        cursor = ObtenerCursor()
        cursor.close()
        cursor.connection.close()

if __name__ == "__main__":
    result = create_tables()
    print(result)