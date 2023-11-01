import unittest
import SecretConfig
import psycopg2
from datetime import datetime
from Card import CreditCard
from CardController import ObtenerCursor, register_credit_card, calculate_payment, make_purchase, get_monthly_payments_report, calculate_amortization_plan

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
            owner_id ="1010123456",
            owner_name ="Comprador compulsivo",
            bank_name ="Bancolombia",
            due_date = "31/12/2027",
            franchise ="VISA",
            payment_day = 10,
            monthly_fee = 24000,
            interest_rate = 3.1,
        )
        with self.assertRaises(ValueError) as context:
            register_credit_card(card_data)
    
    # Verifica si el mensaje de error coincide con el mensaje esperado
        self.assertEqual(str(context.exception), "Tarjeta guardada exitosamente")

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

        with self.assertRaises(ValueError) as context:
            register_credit_card(card_data)
    
    # Verifica si el mensaje de error coincide con el mensaje esperado
        self.assertEqual(str(context.exception), "No se permite guardar la tarjeta porque está vencida")
        

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
        
        with self.assertRaises(ValueError) as context:
            register_credit_card(card_data)
    
    # Verifica si el mensaje de error coincide con el mensaje esperado
        self.assertEqual(str(context.exception), "No permite guardar la tarjeta, porque ya existe")
        

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
        with self.assertRaises(ValueError) as context:
            register_credit_card(card_data)
    
    # Verifica si el mensaje de error coincide con el mensaje esperado
        self.assertEqual(str(context.exception), "Tarjeta guardada exitosamente")
    

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
        with self.assertRaises(ValueError) as context:
            register_credit_card(card_data)
    
    # Verifica si el mensaje de error coincide con el mensaje esperado
        self.assertEqual(str(context.exception), "Tarjeta guardada exitosamente")
      

    def test_payment_normal_case_1(self):
        
        purchase_amount = 200000
        interest_rate = 3.1
        num_installments = 36
        expected_result = 134726.53, 9297.9591

        result = calculate_payment(purchase_amount, interest_rate, num_installments)

        self.assertEqual(result, expected_result)

    def test_payment_normal_case_2(self):
        
        purchase_amount = 850000
        interest_rate = 3.4
        num_installments = 24
        expected_result = 407059.97, 52377.4986

        result = calculate_payment(purchase_amount, interest_rate, num_installments)
        self.assertEqual(result, expected_result)

    def test_payment_zero_interest_rate(self):
        # Caso de prueba con tasa de interés cero - Zero Interest Rate Test Case
        purchase_amount = 480000
        interest_rate = 0
        num_installments = 48
        expected_result = 0.00, 10000.0000

        result = calculate_payment(purchase_amount, interest_rate, num_installments)

        self.assertEqual(result, expected_result)

    def test_payment_single_installment(self):
        # Caso de prueba con una sola cuota - Single Fee Test Case
        purchase_amount = 90000
        interest_rate = 2.40
        num_installments = 1
        expected_result = 0.00, 90000.0000

        result = calculate_payment(purchase_amount, interest_rate, num_installments)

        self.assertEqual(result, expected_result)

    def test_payment_error_zero_purchase_amount(self):
        purchase_amount = 0
        interest_rate = 3.4
        num_installments = 60
        expected_result = "Error: El Monto debe ser superior a cero"
        result = calculate_payment(purchase_amount, interest_rate, num_installments)

        self.assertEqual(result, expected_result)

    def test_payment_error_negative_installments(self):
        # Caso de prueba con número de cuotas negativo - Test case with negative odds number
        purchase_amount = 50000
        interest_rate = 3.0
        num_installments = -10
        expected_result = "Error: El numero de cuotas debe ser mayor a cero"

        result = calculate_payment(purchase_amount, interest_rate, num_installments)

        self.assertEqual(result, expected_result)

    def test_payment_error_nonexistent_card(self):
        # Caso de prueba con tarjeta que no existe - Card test case that does not exist
        purchase_amount = 50000
        interest_rate = None
        num_installments = 10
        expected_result = "Error: La tarjeta indicada no existe"

        result = calculate_payment(purchase_amount, interest_rate, num_installments)

        self.assertEqual(result, expected_result)
        
    def test_make_purchase_normal_case(self):
        purchase_amount = 200000
        interest_rate = 0.90
        monthly_payment = 6528.817139

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, 28)

    def test_make_purchase_normal_case_2(self):
        purchase_amount = 850000
        interest_rate = 0.90
        monthly_payment = 39537.78219

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, 20)

    def test_make_purchase_zero_interest(self):
        purchase_amount = 480000
        interest_rate = 0.90
        monthly_payment = 10000

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, 41)

    def test_make_purchase_single_installment(self):
        purchase_amount = 90000
        interest_rate = 0.90
        monthly_payment =  90810

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)
        self.assertEqual(result, 1)
    
    def test_amortization_plan_calculation_1(self):
        card_number = "556677"
        purchase_amount = 200000
        num_installments = 36
        interest_rate = 3.10
        purchase_date = "2023-09-22"
       
        
        # Llama a la función para calcular el plan de amortización
        calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date)
        expected_result = "Cuota mensual = 9297.959116, Total Abonos = 334726.53, Total intereses = 134726.53"

        self.assertAlmostEqual(expected_result, "Cuota mensual = 9297.959116, Total Abonos = 334726.53, Total intereses = 134726.53")

    def test_amortization_plan_calculation_2(self):
        card_number = "223344"
        purchase_amount = 850000
        num_installments = 24
        interest_rate = 3.40
        purchase_date = "2023-09-25"
        
        
        # Llama a la función para calcular el plan de amortización
        calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date)
        expected_result = "Cuota mensual = 52377.49864, Total Abonos = 1257059.96736, Total intereses = 407059.97"

        self.assertAlmostEqual(expected_result, "Cuota mensual = 52377.49864, Total Abonos = 1257059.96736, Total intereses = 407059.97")

    def test_amortization_plan_calculation_tasa_cero(self):
        card_number = "445566"
        purchase_amount = 480000
        num_installments = 48
        interest_rate = 0.00
        purchase_date = "2023-09-29"
        
        # Llama a la función para calcular el plan de amortización
        calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date)
        expected_result = "Cuota mensual = 10000, Total Abonos = 480000.00, Total intereses = 0.00"

        self.assertAlmostEqual(expected_result, "Cuota mensual = 10000, Total Abonos = 480000.00, Total intereses = 0.00")

    def test_amortization_plan_calculation_cuota_unica(self):
        card_number = "445566"
        purchase_amount = 90000
        num_installments = 1
        interest_rate = 0.00
        purchase_date = "2023-11-17"
        
        # Llama a la función para calcular el plan de amortización
        calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date)
        expected_result = "Cuota mensual = 10000, Total Abonos = 10000.00, Total intereses = 0.00"

        self.assertAlmostEqual(expected_result, "Cuota mensual = 10000, Total Abonos = 10000.00, Total intereses = 0.00")

    def test_get_monthly_payments_report_1(self):
        # Entradas de prueba
        start_date = "2023-10-01"
        end_date = "2023-10-31"

        # Resultado esperado
        expected_result = "Total: 71675.46"

        # Llama a la función y obtén el resultado
        result = get_monthly_payments_report(start_date, end_date)

        # Comprueba si el resultado coincide con el esperado
        self.assertEqual(result, expected_result)
    
    def test_get_monthly_payments_report_2(self):
        # Entradas de prueba
        start_date = "2023-10-01"
        end_date = "2023-12-31"

        # Resultado esperado
        expected_result = "Total: 215026.37"

        # Llama a la función y obtén el resultado
        result = get_monthly_payments_report(start_date, end_date)

        # Comprueba si el resultado coincide con el esperado
        self.assertEqual(result, expected_result)
    
    def test_get_monthly_payments_report_3(self):
        # Entradas de prueba
        start_date = "2026-01-01"
        end_date = "2026-12-31"

        # Resultado esperado
        expected_result = "Total: 203681.63"

        # Llama a la función y obtén el resultado
        result = get_monthly_payments_report(start_date, end_date)

        # Comprueba si el resultado coincide con el esperado
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()