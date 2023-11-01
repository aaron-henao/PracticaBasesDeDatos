from flask import Flask, request, jsonify, render_template
from SecretConfig import DATABASE, USER, PASSWORD, HOST, PORT
import psycopg2
from Card import CreditCard
from CardController import register_credit_card, calculate_payment, make_purchase, calculate_amortization_plan
import CardController
import traceback
from Card import CreditCard

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

@app.route('/view/new-card')
def VistaAgregarTajeta():
    return render_template("new-card.html")

@app.route("/view/save-card")
def VistaGuardarTarjeta():
    try:
        
        card_number = request.args["card_number"]
        owner_id = request.args["owner_id"]
        owner_name = request.args["owner_name"]
        bank_name = request.args["bank_name"]
        due_date = request.args["due_date"]
        franchise = request.args["franchise"]
        payment_day = int(request.args["payment_day"])
        monthly_fee = float(request.args["monthly_fee"])
        interest_rate = float(request.args["interest_rate"])

        new_card = CreditCard(card_number, owner_id,owner_name,bank_name,due_date,franchise,payment_day,monthly_fee,interest_rate)
        CardController.register_credit_card( new_card) 
        return f"La tarjeta {card_number} se ha agregado correctamente"
        
    
    except Exception as e:
        error_message = f"Error al agregar la tarjeta {card_number}: {str(e)}"
        traceback.print_exc()  # Imprime la traza de la excepción para depuración
        return error_message
    

@app.route("/view/purchase-simulate")
def VistaSimularCompra():
    purchase_amount = float(request.args["purchase_amount"])
    card_number = request.args["card_number"]
    num_installments = int(request.args["num_installments"])

    cursor = ObtenerCursor()
    cursor.execute(f"""select interest_rate from credit_card where card_number='{card_number}'""")
    interest_rate = float(cursor.fetchone()[0])

    compra = calculate_payment(purchase_amount, interest_rate, num_installments)
    CardController.calculate_payment(compra)
    return compra


@app.route("/view/simulate-saving")
def VistaAhorroProgramado():
    purchase_amount = float(request.args["purchase_amount"])
    monthly_payment = float(request.args["monthly_payment"])
    interest_rate = float(request.args["interest_rate"])

    result = make_purchase(purchase_amount, interest_rate, monthly_payment)
    return (f"Número de meses ahorrando: {result}")

@app.route("/view/payment-sheduling")
def VistaProgramacionPagos():
    start_date = request.args[start_date]
    end_date = request.args[end_date]

    total_monthly_payments = CardController.get_monthly_payments_report(start_date, end_date)



    

#WEB SERVICE

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

    new_card = CreditCard(card_number, owner_id,owner_name,bank_name,due_date,franchise,payment_day,monthly_fee,interest_rate)
    CardController.register_credit_card(new_card)
    return {"status": "ok"}
  except:
      return jsonify({"status": "error", "error": "La tarjeta no pudo registrarse"})




  
#http://localhost:5000/api/simulate/purchase?card_number=556677&purchase_amount=20000&num_installments=36  
@app.route("/api/simulate/purchase")
def simulate_purchase():
    try:
        purchase_amount = float(request.args["purchase_amount"])
        card_number = request.args["card_number"]
        num_installments = int(request.args["num_installments"])

        cursor = ObtenerCursor()
        cursor.execute(f"""select interest_rate from credit_card where card_number='{card_number}'""")
        interest_rate = float(cursor.fetchone()[0])


        result = calculate_payment(purchase_amount, interest_rate, num_installments)
        
        return jsonify({
            "status": "ok",
            "total_interest": result[0],
            "monthly_payment": result[1],

        })

    except KeyError:
        return jsonify({
            "status": "error",
            "error": "Parámetros inválidos o faltantes en la solicitud"
        })
    except ValueError as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        })
    except:
        return jsonify({
            "status": "error",
            "error": "Ocurrió un error inesperado"
        })
    


#http://localhost:5000/api/simulate/saving?purchase_amount=200000&monthly_payment=6528.817139&interest_rate=0.90
@app.route("/api/simulate/saving")   
def simulate_saving():
    try:
        purchase_amount = float(request.args["purchase_amount"])
        monthly_payment = float(request.args["monthly_payment"])
        interest_rate = float(request.args["interest_rate"])

        result = make_purchase(purchase_amount, interest_rate, monthly_payment)

        return jsonify({"status": "ok", "months": result})
    
    except:
        return jsonify({
            "status": "error",
            "error": "No es posible hacer el calculo del ahorro programado"
        })
    
#http://localhost:5000/api/purchase/new?card_number=556677&purchase_amount=200000&num_installments=36##&purchase_date=2023-09-22    
@app.route("/api/purchase/new")
def new_purchase():
    
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

        calculate_amortization_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date)


        return jsonify({"status": "ok"})

    except:
        return jsonify({"status": "error", "error": "Ya existe un plan de amortización"})
    
    
if __name__=='__main__':
   CardController.create_tables
   app.run(debug=True) 
    
