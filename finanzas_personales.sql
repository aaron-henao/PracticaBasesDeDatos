create table credit_card(
    card_number varchar(20) not null PRIMARY KEY ,
    owner_id varchar (40) not null,
    owner_name varchar (40) not null,
    bank_name varchar (60)not null,
    due_date date not null,
    franchise varchar (60)not null,
    payment_day int not null,
    monthly_fee float not null,
    interest_rate float not null,
    card_number int (30) not null,

);

create table payment_plan(
    card_number varchar(20) not null PRIMARY KEY,
    purchase_date date not null,
    purchase_amount float not null,
    payment_day int not null,
    payment_amount float not null,
    interest_amount float not null,
    capital_amount float not null,
    balance float not null,
);
