import random
from functions import *
import mysql.connector 
db = mysql.connector.connect(host = 'localhost', user='root', password='admin', database='flipcart')
mycursor = db.cursor()
print("===================================  WELCOME TO FLIPCART  =============================================")

while True:
    print('Options:')
    print('1.Sign up')
    print('2.Login')
    print('3.Exit')
    action = int(input("Enter your choice: "))

    if action==2:
        # admin priviledges
        mycursor.execute('select user,password from admin;')
        admin_list = mycursor.fetchall()
        mycursor.execute('select * from partners;')
        partner_list = mycursor.fetchall()
        mycursor.execute('select user from partners;')
        partner_names = []
        for r in mycursor.fetchall():
            for q in r:
                partner_names.append(q)
        mycursor.execute('select user,password,customer_id from customer;')
        customers = mycursor.fetchall()
        customer_list = []
        for x,y,z in customers:
            l = (x,y)
            customer_list.append(l)
        user = input('Enter username: ')
        password = input('Enter password: ')
        if (user,password) in admin_list:
            print('Admin panel connection established!')
            print('Admin panel:')
            n = int(input('Enter number of items to enter: '))
            for i in range(n):
                name = input('Enter product name: ')
                qty = int(input('Enter quantity: '))
                price = int(input('Enter price: '))
                insert_statement = f"insert into products(name,qty,price) values ('{name}',{qty},{price})"
                mycursor.execute(insert_statement)
            db.commit()

        #customer priviledges
        elif (user,password) in customer_list or user :
            for u,p,id in customers:
                if user == u and password == p:
                    customer_id = id
                    print('Customer panel connection established!')
                    print('Customer Panel:')
                    print('1.To Order')
                    print('2.Order history')
                    choice = int(input('Enter choice: '))
                    if choice == 1:
                        mycursor.execute('Select slno, name, qty, price from products where qty != 0')
                        products = mycursor.fetchall()
                        for index,name,qtyp,price in products:
                            print(f"{index}.Product name:{name}\nPrice:{price}\n")
                        print('Enter your order: ')
                        index = int(input('Enter index: '))
                        qty = int(input('Enter quantity: '))
                        if qty > 10:
                            print('Limit is 10.')
                            qty = int(input('Enter quantity: '))
                        amount = price*qty
                        print(f'Your amount is {amount}')
                        s = f"update products set qty={qtyp - qty} where slno={index}"
                        mycursor.execute(s)
                        db.commit()
                        order_id = generate(6,'s')

                        # add to request
                        request_statement = f"insert into request values({customer_id},'{order_id}', {qty}, {amount}, {index}, 'pending')"
                        mycursor.execute(request_statement)
                        db.commit()
                        shipping_statement = f"insert into shippings values('{order_id}', 'pending', {customer_id})"
                        mycursor.execute(shipping_statement)
                        db.commit()

                        # add to delivery
                        otp = generate(6)
                        dname = random.choice(partner_names)
                        delivery_statement = f"insert into delivery values('{order_id}', {amount}, {customer_id}, {otp}, '{dname}');"
                        mycursor.execute(delivery_statement)
                        db.commit()
                    elif choice == 2:
                        mycursor.execute(f'select * from request where customer_id = {customer_id}')
                        history = mycursor.fetchall()
                        for cid,oid,cqty,cprice,cpid,cstatus in history:
                            mycursor.execute(f'select name from products where slno={cpid}')
                            pnames = mycursor.fetchall()
                            mycursor.execute(f'select otp from delivery where customer_id={cid} and order_id="{oid}"')
                            otps = mycursor.fetchall()
                            cotp = otps[0][0]
                            pname = pnames[0][0]
                            print()
                            print(f'Product name:{pname}')
                            print(f'product:{cpid}')
                            print(f'Amount: {cprice}')
                            print(f'status: {cstatus}')
                            print(f'Your order id is #{oid}')
                            print(f'Your OTP is {cotp}')
        # partners login
            if (user,password) in partner_list:
                mycursor.execute(f'select order_id,amount,customer_id, otp from delivery where dname="{user}"')
                delivery_list = mycursor.fetchall()
                for Order_id,product_amount,customerid,otp in delivery_list:
                    mycursor.execute(f'select address,pin from customer where customer_id={customerid}')
                    address,pin = mycursor.fetchall()[0]
                    mycursor.execute(f'select name from request, products where request.product_id = products.slno and customer_id = {customerid}')
                    product_name = mycursor.fetchall()[0][0]
                    print(f'name:{product_name}\namount:{product_amount}\naddress:{address}\npin:{pin}\n')
                    OTP = int(input('Enter OTP: '))
                    if OTP == otp:
                        print('Product delivered!')
                        s1= f"update shippings set status='delivered' where customer_id={customerid} and shipping_id = '{Order_id}'"
                        s2 = f"update request set status='delivered' where customer_id={customerid} and orderid = '{Order_id}'"
                        mycursor.execute(s1)
                        mycursor.execute(s2)
                        db.commit()
    elif action == 1:
        print('Sign up options:')
        print('1.admin')
        print('2.customer')
        choice = int(input('Enter choice: '))
        user = input('Enter name: ')
        password = input('Enter password: ')
        email = input('Enter email: ')
        if choice == 1:
            address = input('Enter address: ')
            pin = int(input('Enter pin: '))
            mycursor.execute(f"insert into customer(user,password,address,pin,email) values('{user}', '{password}', '{address}', {pin}, '{email}')")
            db.commit()
            print('You are added!')
        elif choice == 2:
            mycursor.execute(f"insert into admin values('{user}', '{password}', '{email}')")
            db.commit()
            print('You are added!')
    elif action == 3:
        print('Thank you for visiting!')
        break
    else:
        print('Invalid choice!\n')