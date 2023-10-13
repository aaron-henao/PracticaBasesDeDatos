from flask import Flask, request, jsonify 
from flask import render_template

from Card import CreditCard
import CardController


@app.route('/params')      
def params():
    return request.args
  
@app.route("/card")
def card():
  try:
    new_card = 


@app.route("/register/card")
def register_card():
  try:
    card_numer = request.args["card_number"]
    owner_id = request.args["owner_id"]
    owner_name = request.args["owner_name"]
    bank_name = request.args["bank_name"]
    due_date = request.args["due_date"]
    franchise = request.args["franchise"]
    payment_day = request.args["payment_day"]
    monthly_fee = request.args["monthly_fee"]
    interest_rate = request.args["interest_rate"]
    
