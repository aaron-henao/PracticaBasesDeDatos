import unittest
import SecretConfig
import psycopg2
from datetime import datetime
from Card import CreditCard
from CardController import ObtenerCursor, register_credit_card, calculate_payment, make_purchase, get_monthly_payments_report

class TestCardController(unittest.TestCase):
    def setUp(self):
        DATABASE = SecretConfig.DATABASE
        USER = SecretConfig.USER
        PASSWORD = SecretConfig.PASSWORD
        HOST = SecretConfig.HOST
        PORT = SecretConfig.PORT
        self.connection = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
        self.controller = self.connection.cursor()

        self.current_date = datetime.now().date()

        

    def tearDown(self):
        # Cierra el cursor y la conexión al final de cada prueba
        # Close the cursor and connection at the end of each test
        self.controller.close()
        self.connection.close()

   
    def test_register_credit_card_T1(self):
        card_data = CreditCard(
            card_number="556677",
            owner_id="1010123456",
            owner_name="Comprador compulsivo",
            bank_name="Bancolombia",
            due_date= "31/12/2027",
            franchise="VISA",
            payment_day=10,
            monthly_fee=24000,
            interest_rate=3.1,
        )
        # Pasar el objeto card_data como único argumento
        # Pass object card_data as the only argument
        result = register_credit_card(card_data)  
        self.assertEqual(result, "Tarjeta guardada exitosamente")

    def test_register_credit_card_T2(self):
        card_data = CreditCard(
            card_number = "442233",
            owner_id = "1010123456",
            owner_name = "Comprador compulsivo",
            bank_name = "Popular",
            due_date="31/12/2022",
            franchise = "Mastercard",
            payment_day = 5,
            monthly_fee = 34000,
            interest_rate = 3.4,
        )
        
        result = register_credit_card(card_data)
        self.assertEqual(result, "No se permite guardar la tarjeta porque está vencida")

    def test_register_credit_card_T3(self):
        card_data = CreditCard(
            card_number = "556677",
            owner_id = "1020889955",
            owner_name ="Estudiante pelao",
            bank_name = "Bancolombia",
            due_date= "31/12/2027", 
            franchise = "VISA",
            payment_day = 10,
            monthly_fee = 24000,
            interest_rate = 3.1,
        )
        
        result = register_credit_card(card_data)
        self.assertEqual(result, "No permite guardar la tarjeta, porque ya existe")

    def test_register_credit_card_T4(self):
        card_data = CreditCard(
            card_number ="223344",
            owner_id = "1010123456",
            owner_name = "Comprador compulsivo",
            bank_name = "Falabella",
            due_date= "31/12/2025", 
            franchise = "VISA",
            payment_day = 16,
            monthly_fee = 0,
            interest_rate = 3.4,
        )
        
        result = register_credit_card(card_data)
        self.assertEqual(result, "Tarjeta guardada exitosamente")

    def test_register_credit_card_T5(self):
        card_data = CreditCard(
            card_number ="445566",
            owner_id = "1010123456",
            owner_name = "Comprador compulsivo",
            bank_name = "BBVA",
            due_date="31/12/2027",
            franchise = "Mastercard",
            payment_day = 5,
            monthly_fee = 34000,
            interest_rate = 0,
        )
        
        result = register_credit_card(card_data)
        self.assertEqual(result, "Tarjeta guardada exitosamente")

    def test_payment_normal_case_1(self):
        
        purchase_amount = 200000
        card = {"interest_rate": 3.1}
        num_installments = 36
        expected_result = "Total Intereses: 134726.53 - Cuota: 9297.9591"

        result = calculate_payment(purchase_amount, card, num_installments)

        # Redondear los resultados antes de compararlos
        # Round up results before comparing
        expected_result = expected_result.replace(" ", "").split("-")
        expected_result = [round(float(item.split(":")[1]), 2) for item in expected_result]
        result = result.replace(" ", "").split("-")
        result = [round(float(item.split(":")[1]), 2) for item in result]

        self.assertEqual(result, expected_result)

    def test_payment_normal_case_2(self):
        
        purchase_amount = 850000
        card = {"interest_rate": 3.4}
        num_installments = 24
        expected_result = "Total Intereses: 407059.97 - Cuota: 52377.4986"

        result = calculate_payment(purchase_amount, card, num_installments)

        # Redondear los resultados antes de compararlos
        # Round up results before comparing
        expected_result = expected_result.replace(" ", "").split("-")
        expected_result = [round(float(item.split(":")[1]), 2) for item in expected_result]
        result = result.replace(" ", "").split("-")
        result = [round(float(item.split(":")[1]), 2) for item in result]

        self.assertEqual(result, expected_result)

    def test_payment_zero_interest_rate(self):
        # Caso de prueba con tasa de interés cero - Zero Interest Rate Test Case
        purchase_amount = 480000
        card = {"interest_rate": 0}
        num_installments = 48
        expected_result = "Total Intereses: 0.00 - Cuota: 10000.00"

        result = calculate_payment(purchase_amount, card, num_installments)

        # Redondear los resultados antes de compararlos
        # Round up results before comparing
        expected_result = expected_result.replace(" ", "").split("-")
        expected_result = [round(float(item.split(":")[1]), 2) for item in expected_result]
        result = result.replace(" ", "").split("-")
        result = [round(float(item.split(":")[1]), 2) for item in result]

        self.assertEqual(result, expected_result)

    def test_payment_single_installment(self):
        # Caso de prueba con una sola cuota - Single Fee Test Case
        purchase_amount = 90000
        card = {"interest_rate": 5.2}
        num_installments = 1
        expected_result = "Total Intereses: 0.00 - Cuota: 90000.00"

        result = calculate_payment(purchase_amount, card, num_installments)

        # Redondear los resultados antes de compararlos
        # Round up results before comparing
        expected_result = expected_result.replace(" ", "").split("-")
        expected_result = [round(float(item.split(":")[1]), 2) for item in expected_result]
        result = result.replace(" ", "").split("-")
        result = [round(float(item.split(":")[1]), 2) for item in result]

        self.assertEqual(result, expected_result)

    def test_payment_error_zero_purchase_amount(self):
        purchase_amount = 0
        card = {
            "interest_rate": 3.4
        }
        num_installments = 60
        expected_result = "Error: El Monto debe ser superior a cero"
        result = calculate_payment(purchase_amount, card, num_installments)

        self.assertEqual(result, expected_result)

    def test_payment_error_negative_installments(self):
        # Caso de prueba con número de cuotas negativo - Test case with negative odds number
        purchase_amount = 50000
        card = {"interest_rate": 3.0}
        num_installments = -10
        expected_result = "Error: El numero de cuotas debe ser mayor a cero"

        result = calculate_payment(purchase_amount, card, num_installments)

        self.assertEqual(result, expected_result)

    def test_payment_error_nonexistent_card(self):
        # Caso de prueba con tarjeta que no existe - Card test case that does not exist
        purchase_amount = 50000
        card = {"interest_rate": None}  
        num_installments = 10
        expected_result = "Error: La tarjeta indicada no existe"

        result = calculate_payment(purchase_amount, card, num_installments)

        self.assertEqual(result, expected_result)
        
    def test_make_purchase_normal_case(self):
        purchase_amount = 200000
        interest_rate = 0.90
        monthly_payment = 6528.817139

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, "Número de meses ahorrando: 28")

    def test_make_purchase_normal_case_2(self):
        purchase_amount = 850000
        interest_rate = 0.90
        monthly_payment = 39537.78219

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, "Número de meses ahorrando: 20")

    def test_make_purchase_zero_interest(self):
        purchase_amount = 480000
        interest_rate = 0.90
        monthly_payment = 10000

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, "Número de meses ahorrando: 41")

    def test_make_purchase_single_installment(self):
        purchase_amount = 90000
        interest_rate = 0.90
        monthly_payment =  90810

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, "Número de meses ahorrando: 1")
    
    def test_get_monthly_payments_report(self):
        # Entradas de prueba
        card_number = "223344 Falabella"
        start_date = "2023-10-01"
        end_date = "2023-10-31"

        # Resultado esperado
        expected_result = "Total cuotas : 71,675"

        # Llama a la función y obtén el resultado
        result = get_monthly_payments_report(card_number, start_date, end_date)

        # Comprueba si el resultado coincide con el esperado
        self.assertEqual(result, expected_result)

   
if __name__ == '__main__':
    unittest.main()