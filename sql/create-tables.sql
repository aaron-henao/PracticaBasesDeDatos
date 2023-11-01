create table credit_card(
    card_number VARCHAR(16),
    owner_id VARCHAR(10),
    owner_name VARCHAR(255),
    bank_name VARCHAR(255),
    due_date DATE,
    franchise VARCHAR(255),
    payment_day INTEGER,
    monthly_fee FLOAT,
    interest_rate FLOAT
);

create table payment_plan (
    card_number varchar(20) not null,
    purchase_date date not null,
    payment_date date not null,
    purchase_amount float not null,
    payment_amount float not null,
    interest_amount float not null,
    capital_amount float not null,
    balance float not null
);
