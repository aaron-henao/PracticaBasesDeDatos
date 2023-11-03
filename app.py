from flask import Flask, request, jsonify, render_template
from SecretConfig import DATABASE, USER, PASSWORD, HOST, PORT
import psycopg2
from Card import CreditCard
from CardController import calculate_payment, make_purchase, calculate_amortization_plan, calculate_plan, get_monthly_payments_reports
import CardController
from Card import CreditCard
from datetime import datetime

app = Flask(__name__)     

def ObtenerCursor():
    """
    Crea la conexión a la base de datos y devuelve un cursor para ejecutar instrucciones.
    """
    connection = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
    return connection.cursor()

@app.route("/")
def Home():
    return render_template("index.html")

@app.route('/view/new-card')
def VistaAgregarTajeta():
    return render_template("new-card.html")

@app.route("/view/save-card")
def VistaGuardarTarjeta():
    
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
    CardController.insert_card(new_card)
    return f"La tarjeta {card_number} se ha agregado correctamente"
       
@app.route("/view/purchase")
def VistaSimularCompra():
    return render_template("purchase-simulate.html")


@app.route("/view/purchase-simulate")
def SimularCompra():

    purchase_amount = float(request.args["purchase_amount"])
    card_number = request.args["card_number"]
    num_installments = int(request.args["num_installments"])

    cursor = ObtenerCursor()
    cursor.execute(f"""select interest_rate from credit_card where card_number='{card_number}'""")
    interest_rate = float(cursor.fetchone()[0])

    CardController.calculate_payment(purchase_amount, interest_rate, num_installments)
    compra = calculate_payment(purchase_amount, interest_rate, num_installments)
    return f"Total Intereses: {compra[0]} - Cuota: {compra[1]}"


@app.route("/view/saving")
def VistaAhorroProgramado():
    return render_template("simulate-saving.html")

@app.route("/view/simulate-saving")
def AhorroProgramado():
    purchase_amount = float(request.args["purchase_amount"])
    monthly_payment = float(request.args["monthly_payment"])
    interest_rate = float(request.args["interest_rate"])

    result = make_purchase(purchase_amount, interest_rate, monthly_payment)
    return (f"Número de meses ahorrando: {result}")

@app.route("/view/plan")
def VistaPlan():
    return render_template("payment-register.html")

@app.route("/view/payment-register")
def PlanAmortizacion():
    card_number = request.args["card_number"]
    purchase_amount = float(request.args["purchase_amount"])
    num_installments = int(request.args["num_installments"])
    interest_rate = float(request.args["interest_rate"])
    purchase_date = request.args["purchase_date"]

    result = calculate_plan(card_number, purchase_amount, num_installments, interest_rate, purchase_date)
    CardController.insert_plan(result)
    return "El plan de amortización se almacenó con éxito"


@app.route("/view/payment")
def VerPago():
    return render_template("payment-sheduling.html")

@app.route("/view/payment-sheduling")
def VistaProgramacionPagos():
    start_date = request.args["start_date"]
    end_date= request.args["end_date"]
    owner_id = request.args["owner_id"]


    result = get_monthly_payments_reports(start_date, end_date, owner_id)
    return result


@app.route("/view/delete")
def VistaEliminar():
    return render_template("delete-card.html")

@app.route("/view/delete-card")
def VistaElminiarTarjeta():
    card_number = request.args["card_number"]
    CardController.delete_card(card_number)
    return f"Tarjeta {card_number} eliminada con éxito"

if __name__=='__main__':
   CardController.create_tables()
   app.run(debug=True) 
    
