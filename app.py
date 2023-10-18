from flask import Flask, request, jsonify 
from flask import render_template
from SecretConfig import DATABASE, USER, PASSWORD, HOST, PORT
from datetime import datetime, timedelta
import psycopg2
from CardController import checkInterest, calculate_fee_payment, calculate_amortization_plan


app = Flask(__name__)     

def ObtenerCursor():
    """
    Crea la conexión a la base de datos y devuelve un cursor para ejecutar instrucciones.
    """
    connection = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    return connection.cursor()

@app.route('/params')      
def params():
    return request.args

#http://localhost:5000/api/card/new?card_number=556677&owner_id=1010123456&owner_name=Comprador compulsivo&bank_name=Bancolombia&due_date=2027-12-31&franchise=VISA&payment_day=10&monthly_fee=24000.00&interest_rate=3.10
@app.route("/api/card/new")
def register_card():
  try:
    card_number = request.args["card_number"]
    owner_id = request.args["owner_id"]
    owner_name = request.args["owner_name"]
    bank_name = request.args["bank_name"]
    due_date = request.args["due_date"]
    franchise = request.args["franchise"]
    payment_day = request.args["payment_day"]
    monthly_fee = request.args["monthly_fee"]
    interest_rate = request.args["interest_rate"]
    cursor = ObtenerCursor()

        # Verificar si la tarjeta ya está registrada
    cursor.execute("SELECT * FROM credit_card WHERE card_number = %s", (card_number,))
    existing_card = cursor.fetchone()

    if existing_card:
        cursor.close()
        return {"status": "error", "message": "La tarjeta ya está registrada"}

        # Insertar la nueva tarjeta en la base de datos
    cursor.execute("INSERT INTO credit_card (card_number, owner_id, owner_name, bank_name, due_date, franchise, payment_day, monthly_fee, interest_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                       (card_number, owner_id, owner_name, bank_name, due_date, franchise, payment_day, monthly_fee, interest_rate))
    cursor.connection.commit()
    cursor.close()

    return {"status": "ok"}

  except Exception as e:
      return {"status": "error", "message": str(e)}
  
#http://localhost:5000/api/simulate/purchase?card_number=556677&purchase_amount=20000&num_installments=36  
@app.route("/api/simulate/purchase")
def simulate_purchase():
    try:
        purchase_amount = float(request.args["purchase_amount"])
        card_number = request.args["card_number"]
        num_installments = int(request.args["num_installments"])
        cursor = ObtenerCursor()

        cursor.execute("SELECT * FROM credit_card WHERE card_number = %s", (card_number,))
        result = cursor.fetchone()

        if result:
            card = {
                "card_number": result[0],
                "owner_id": result[1],
                "owner_name": result[2],
                "bank_name": result[3],
                "due_date": result[4],
                "franchise": result[5],
                "payment_day": result[6],
                "monthly_fee": float(result[7]),  # Convertir a float
                "interest_rate": float(result[8])  # Convertir a float
            }
        else:
            raise Exception("Error: La tarjeta indicada no existe")

        if purchase_amount <= 0:
            raise Exception("Error: El Monto debe ser superior a cero")

        interest_rate: float = card.get("interest_rate")

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

            # Redondear monthly_payment a 4 decimales para obtener 9297.9591
            monthly_payment = round(monthly_payment, 4)

            total_interest = (monthly_payment * num_installments) - purchase_amount

        return jsonify({"status": "ok", "monthly_payment": monthly_payment, "total_interest": round(total_interest, 2)})
    except Exception as e:
        return {"status": "error", "message": str(e)}


#http://localhost:5000/api/simulate/saving?purchase_amount=200000&monthly_payment=6528.817139&interest_rate=0.90
@app.route("/api/simulate/saving")   
def simulate_saving():
    try:
        purchase_amount = float(request.args["purchase_amount"])
        monthly_payment = float(request.args["monthly_payment"])
        interest_rate = float(request.args["interest_rate"])

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
             return jsonify({"status": "ok", "months": num_months})
        
    
        return jsonify({"status": "ok", "months": num_months})
    except Exception as e:
        return str(e)
    
#http://localhost:5000/api/purchase/new?card_number=556677&purchase_amount=200000&num_installments=36##&purchase_date=2023-09-22    
@app.route("/api/purchase/new", methods=['GET', 'POST'])
def new_purchase():
    if request.method == 'POST':
        # Procesa la solicitud POST
        try:
            card_number = request.args.get("card_number")
            purchase_amount = float(request.args.get("purchase_amount"))
            num_installments = int(request.args.get("payments"))
            purchase_date = request.args.get("purchase_date")

            cursor = ObtenerCursor()

            # Obtener la tasa de interés de la tarjeta
            cursor.execute("SELECT interest_rate FROM credit_card WHERE card_number = %s", (card_number,))
            row = cursor.fetchone()

            if row is None:
                return {"status": "error", "message": "La tarjeta indicada no existe"}

            interest_rate = float(row[0])

            # Calcula el plan de amortización
            _, _, _ = calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date)

            cursor.connection.commit()
            cursor.close()
            cursor.connection.close()

            return jsonify({"status": "ok"})

        except Exception as e:
            return {"status": "error", "message": str(e)}
    else:
        # Aquí puedes manejar la solicitud GET (si es necesario) o simplemente retornar un mensaje
        return jsonify({"status": "ok"})
    
if __name__=='__main__':
   app.run() 
    
