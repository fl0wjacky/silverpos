from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.lang import Builder

from collections import OrderedDict
import mysql.connector
from pymongo import MongoClient
from utils.datatable import DataTable
from datetime import datetime
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg as FCK

Builder.load_file('admin/admin.kv')


class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (.7,.7)

class AdminWindow(BoxLayout):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.notify = Notify()

        self.db = db
        if self.db == 'mongo':
            # MongoDB
            client = MongoClient()
            db = client.silverpos
            self.users = db.users
            self.stocks = db.stocks
            users = self.mongo_get_users()
            products = self.mongo_get_products()

        elif self.db == 'mysql':
            # MySQL
            self.mydb = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='youcantguessme',
                database='pos'
            )
            self.mycursor = self.mydb.cursor()
            users = self.mysql_get_users()
            products = self.mysql_get_products()
        else:
            pass

        #print(self.get_products())
        content = self.ids.scrn_contents
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        # Display Products
        product_scrn = self.ids.scrn_product_contents
        prod_table = DataTable(table=products)
        product_scrn.add_widget(prod_table)

        # Analysis
        spinvalues = []
        for i in range(len(products['product_code'])):
            line = ' | '.join([products['product_code'][i], products['product_name'][i]])
            spinvalues.append(line)
        else:
            self.ids.target_products.values = spinvalues

    def logout(self):
        self.parent.parent.current = 'scrn_si'

    # mongodb
    def mongo_get_users(self):
        users = self.users
        _users = OrderedDict()
        _users['first_names'] = {}
        _users['last_names'] = {}
        _users['user_names'] = {}
        _users['passwords'] = {}
        _users['designations'] = {}
        first_names = []
        last_names = []
        user_names = []
        passwords = []
        designations = []

        for user in users.find():
            first_names.append(user['first_name'])
            last_names.append(user['last_name'])
            user_names.append(user['user_name'])
            pwd = user['password']
            if len(pwd) > 10:
                pwd = pwd[:10] + '...'
            passwords.append(pwd)
            designations.append(user['designation'])
        #print(designations)
        users_length = len(first_names)
        for i in range(0, users_length):
            _users['first_names'][i] = first_names[i]
            _users['last_names'][i] = last_names[i]
            _users['user_names'][i] = user_names[i]
            _users['passwords'][i] = passwords[i]
            _users['designations'][i] = designations[i]

        return _users

    def mongo_get_products(self):
        stocks = self.stocks
        _stocks = OrderedDict()
        _stocks['product_code'] = {}
        _stocks['product_name'] = {}
        _stocks['product_weight'] = {}
        #_stocks['product_price'] = {}
        _stocks['in_stock'] = {}
        _stocks['sold'] = {}
        _stocks['order'] = {}
        _stocks['last_purchase'] = {}
        #_stocks['ordered'] = {}
        product_code = []
        product_name = []
        product_weight = []
        #product_price = []
        in_stock = []
        sold = []
        order = []
        last_purchase = []
        #ordered = []

        for stock in stocks.find():
            product_code.append(stock['product_code'])
            name = stock['product_name']
            if len(name) > 10:
                name = name[:10] + '...'
            product_name.append(name)
            product_weight.append(stock['product_weight'])
            #product_price.append(stock['product_price'])
            in_stock.append(stock['in_stock'])
            try:
                sold.append(stock['sold'])
            except KeyError:
                sold.append('')
            try:
                order.append(stock['order'])
            except KeyError:
                order.append('')
            try:
                last_purchase.append(stock['last_purchase'])
            except KeyError:
                last_purchase.append('')
            #ordered.append(stock['ordered'])
        stocks_length = len(product_code)
        for i in range(0, stocks_length):
            _stocks['product_code'][i] = product_code[i]
            _stocks['product_name'][i] = product_name[i]
            _stocks['product_weight'][i] = product_weight[i]
            #_stocks['product_price'][i] = product_price[i]
            _stocks['in_stock'][i] = in_stock[i]
            _stocks['sold'][i] = sold[i]
            _stocks['order'][i] = order[i]
            _stocks['last_purchase'][i] = last_purchase[i]
            #_stocks['ordered'][i] = ordered[i]

        return _stocks

    # for mysql
    def mysql_get_users(self):
        mycursor = self.mycursor
        _users = OrderedDict()
        _users['first_names'] = {}
        _users['last_names'] = {}
        _users['user_names'] = {}
        _users['passwords'] = {}
        _users['designations'] = {}
        first_names = []
        last_names = []
        user_names = []
        passwords = []
        designations = []
        sql = "SELECT first_name,last_name,user_name,password,designation FROM users;"
        mycursor.execute(sql)
        users = mycursor.fetchall()
        for user in users:
            first_names.append(user[0])
            last_names.append(user[1])
            user_names.append(user[2])
            pwd = user[3]
            if len(pwd) > 10:
                pwd = pwd[:10] + '...'
            passwords.append(pwd)
            designations.append(user[4])
        #print(designations)
        users_length = len(first_names)
        for i in range(0, users_length):
            _users['first_names'][i] = first_names[i]
            _users['last_names'][i] = last_names[i]
            _users['user_names'][i] = user_names[i]
            _users['passwords'][i] = passwords[i]
            _users['designations'][i] = designations[i]

        return _users

    def mysql_get_products(self):
        mycursor = self.mycursor
        _stocks = OrderedDict()
        _stocks['product_code'] = {}
        _stocks['product_name'] = {}
        _stocks['product_weight'] = {}
        #_stocks['product_price'] = {}
        _stocks['in_stock'] = {}
        _stocks['sold'] = {}
        _stocks['order'] = {}
        _stocks['last_purchase'] = {}
        #_stocks['ordered'] = {}
        product_code = []
        product_name = []
        product_weight = []
        #product_price = []
        in_stock = []
        sold = []
        order = []
        last_purchase = []
        #ordered = []
        sql = 'SELECT product_code,product_name,product_weight,in_stock,sold,ordered,last_purchase FROM stocks;'
        mycursor.execute(sql)
        stocks = mycursor.fetchall()
        for stock in stocks:
            product_code.append(stock[0])
            name = stock[1]
            if len(name) > 10:
                name = name[:10] + '...'
            product_name.append(name)
            product_weight.append(stock[2])
            #product_price.append(stock['product_price'])
            in_stock.append(stock[3])
            sold.append(stock[4])
            order.append(stock[5])
            last_purchase.append(stock[6])
            #ordered.append(stock['ordered'])
        stocks_length = len(product_code)
        for i in range(0, stocks_length):
            _stocks['product_code'][i] = product_code[i]
            _stocks['product_name'][i] = product_name[i]
            _stocks['product_weight'][i] = product_weight[i]
            #_stocks['product_price'][i] = product_price[i]
            _stocks['in_stock'][i] = in_stock[i]
            _stocks['sold'][i] = sold[i]
            _stocks['order'][i] = order[i]
            _stocks['last_purchase'][i] = last_purchase[i]
            #_stocks['ordered'][i] = ordered[i]

        return _stocks

    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'
        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'
        else:
            self.ids.scrn_mngr.current = 'scrn_analysis'

    def add_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='Frist Name',multiline=False)
        crud_last = TextInput(hint_text='Last Name',multiline=False)
        crud_user = TextInput(hint_text='User Name',multiline=False)
        crud_pwd = TextInput(hint_text='Password',multiline=False)
        crud_des = Spinner(text='Operator', values=['Operator','Administrator'])
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
            on_release=lambda x: self.add_user(
                crud_first.text,
                crud_last.text,
                crud_user.text,
                crud_pwd.text,
                crud_des.text
            ))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def add_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text='Code',multiline=False)
        crud_name = TextInput(hint_text='Name',multiline=False)
        crud_weight = TextInput(hint_text='Weight',multiline=False)
        crud_stock = TextInput(hint_text='In Stock',multiline=False)
        crud_sold  = TextInput(hint_text='Sold',multiline=False)
        curd_ordered = TextInput(hint_text='Ordered',multiline=False)
        curd_purchase = TextInput(hint_text='Last Purchase',multiline=False)
        crud_submit = Button(text='Add', size_hint_x=None, width=100,
            on_release=lambda x:self.add_product(
                crud_code.text,
                crud_name.text,
                crud_weight.text,
                crud_stock.text,
                crud_sold.text,
                curd_ordered.text,
                curd_purchase.text
            ))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_weight)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(curd_ordered)
        target.add_widget(curd_purchase)
        target.add_widget(crud_submit)

    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text='Code',multiline=False)
        crud_name = TextInput(hint_text='Name',multiline=False)
        crud_weight = TextInput(hint_text='Weight',multiline=False)
        crud_stock = TextInput(hint_text='In Stock',multiline=False)
        crud_sold  = TextInput(hint_text='Sold',multiline=False)
        curd_ordered = TextInput(hint_text='Ordered',multiline=False)
        curd_purchase = TextInput(hint_text='Last Purchase',multiline=False)
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
            on_release=lambda x:self.update_product(
                crud_code.text,
                crud_name.text,
                crud_weight.text,
                crud_stock.text,
                crud_sold.text,
                curd_ordered.text,
                curd_purchase.text
            ))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_weight)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(curd_ordered)
        target.add_widget(curd_purchase)
        target.add_widget(crud_submit)

    def update_product(self, code, name, weight, stock, sold, ordered, purchase):
        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Product Code[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return
        else:
            # MongoDB
            if self.db == 'mongo':
                m_product = self.stocks.find_one({'product_code':code})
                if m_product is None:
                    self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Product Code[/b][/color]', markup=True))
                    self.notify.open()
                    Clock.schedule_once(self.killswitch, 1)
                    return
                if name  ==  '': name = m_product['product_name']
                if weight == '': weight = m_product['product_weight']
                if stock  == '': stock = m_product['in_stock']
                if sold  ==  '': sold = m_product['sold']
                if ordered == '': ordered = m_product['ordered']
                if purchase == '': purchase = m_product['last_purchase']
            # MySQL
            elif self.db == 'mysql':
                pass
            else:
                pass


        if self.db == 'mongo':
            # MongoDB
            self.stocks.update_one(
                {'product_code':code},
                {'$set':{
                    'product_name':name,
                    'product_weight':weight,
                    'in_stock':int(stock),
                    'sold':int(sold),
                    'order':ordered,
                    'ordered':ordered,
                    'last_purchase':purchase
                }})
            products = self.mongo_get_products()
        elif self.db == 'mysql':
            # MySQL
            sql = "UPDATE stocks SET procuct_name=%s,product_weight=%s,in_stock=%s,sold=%s,ordered=%s,last_purchase=% WHERE product_code=%s"
            values = [name,weight,stock,sold,ordered,purchase,code]
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            products = self.mysql_get_products()
        else:
            pass
        
        content = self.ids.scrn_product_contents
        content.clear_widgets()
        productstable = DataTable(table=products)
        content.add_widget(productstable)

    def add_product(self, code, name, weight, stock, sold, ordered, purchase):
        if map(lambda x:x=='',[code,name,weight,stock,sold,ordered,purchase]):
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return

        if self.db == 'mongo':
            # MongoDB
            self.stocks.insert_one({
                'product_code':code,
                'product_name':name,
                'product_weight':weight,
                'in_stock':int(stock) if stock else 0,
                'sold':int(sold) if sold else 0,
                'order':ordered,
                'ordered':ordered,
                'last_purchase':purchase
                })
            products = self.mongo_get_products()
        elif self.db == 'mysql':
            # MySQL
            sql = "INSERT INTO stocks(product_code,product_name,product_weight,in_stock,sold,ordered,last_purchase) VALUES(%s,%s,%s,%s,%s,%s);"
            values = [code,name,weight,stock,sold,ordered,purchase]
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            products = self.mysql_get_products()
        else:
            pass
        
        content = self.ids.scrn_product_contents
        content.clear_widgets()
        productstable = DataTable(table=products)
        content.add_widget(productstable)

    def update_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='Frist Name',multiline=False)
        crud_last = TextInput(hint_text='Last Name',multiline=False)
        crud_user = TextInput(hint_text='User Name',multiline=False)
        crud_pwd = TextInput(hint_text='Password',multiline=False)
        crud_des = Spinner(text='Operator', values=['Operator','Administrator'])
        crud_submit = Button(text='Update', size_hint_x=None, width=100,
            on_release=lambda x: self.update_user(
                crud_first.text,
                crud_last.text,
                crud_user.text,
                crud_pwd.text,
                crud_des.text
            ))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)

    def remove_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_user = TextInput(hint_text='User Name',multiline=False)
        crud_submit = Button(text='Remove', size_hint_x=None, width=200,
            on_release=lambda x: self.remove_user(crud_user.text))

        target.add_widget(crud_user)
        target.add_widget(crud_submit)

    def remove_user(self, user):
        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Username[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return
        else:
            # MongoDB
            if self.db == 'mongo':
                m_user = self.users.find_one({"user_name":user})
                if m_user is None:
                    self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Username[/b][/color]', markup=True))
                    self.notify.open()
                    Clock.schedule_once(self.killswitch, 1)
                    return
            # MySQL
            elif self.db == 'mysql':
                pass
            else:
                pass

        content = self.ids.scrn_contents
        content.clear_widgets()

        if self.db == 'mongo':
            # MongoDB
            self.users.remove({'user_name':user})
            users = self.mongo_get_users()
        elif self.db == 'mysql':
            # MySQL
            sql = "DELETE FROM users WHERE user_name=%s"
            values = [user]
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            users = self.mysql_get_users()
        else:
            pass
        
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    def add_user(self, first, last, user, pwd, des):
        pwd = hashlib.sha256(pwd.encode()).hexdigest()
        if first == '' or last == '' or user == '' or pwd == '' or des == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]All Fields Required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return

        if self.db == 'mongo':
            # MongoDB
            self.users.insert_one({
                'first_name':first,
                'last_name':last,
                'user_name':user,
                'password':pwd,
                'designation':des,
                'date':datetime.now()
                })
            users = self.mongo_get_users()
        elif self.db == 'mysql':
            # MySQL
            sql = "INSERT INTO users(first_name,last_name,user_name,password,designation,date) VALUES(%s,%s,%s,%s,%s,%s);"
            values = [first,last,user,pwd,des,datetime.now()]
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            users = self.mysql_get_users()
        else:
            pass
        
        content = self.ids.scrn_contents
        content.clear_widgets()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def update_user(self, first, last, user, pwd, des):
        if user == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Username[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return
        else:
            # MongoDB
            if self.db == 'mongo':
                m_user = self.users.find_one({"user_name":user})
                if m_user is None:
                    self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Username[/b][/color]', markup=True))
                    self.notify.open()
                    Clock.schedule_once(self.killswitch, 1)
                    return
                if first == '': first = m_user['first_name']
                if last == '': last = m_user['last_name']
                if pwd == '': pwd = m_user['password']
                if des == '': des = m_user['designation']
            # MySQL
            elif self.db == 'mysql':
                pass
            else:
                pass

        content = self.ids.scrn_contents
        content.clear_widgets()
        pwd = hashlib.sha256(pwd.encode()).hexdigest()

        if self.db == 'mongo':
            # MongoDB
            self.users.update_one(
                {'user_name':user},
                {'$set':{
                    'first_name':first,
                    'last_name':last,
                    'password': pwd,
                    'designation': des,
                    'date':datetime.now()
                }})
            users = self.mongo_get_users()
        elif self.db == 'mysql':
            # MySQL
            sql = "UPDATE users SET first_name=%s,last_name=%s,user_name=%s,password=%s,designation=%s WHERE user_name=%s"
            values = [first,last,user,pwd,des,user]
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            users = self.mysql_get_users()
        else:
            pass
        
        userstable = DataTable(table=users)
        content.add_widget(userstable)

    def remove_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text='Product Code',multiline=False)
        crud_submit = Button(text='Remove', size_hint_x=None, width=200,
            on_release=lambda x: self.remove_product(crud_code.text))

        target.add_widget(crud_code)
        target.add_widget(crud_submit)

    def remove_product(self, code):
        if code == '':
            self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Product Code[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
            return
        else:
            # MongoDB
            if self.db == 'mongo':
                m_product = self.stocks.find_one({'product_code':code})
                if m_product is None:
                    self.notify.add_widget(Label(text='[color=#FF0000][b]Invalid Product Code[/b][/color]', markup=True))
                    self.notify.open()
                    Clock.schedule_once(self.killswitch, 1)
                    return
            # MySQL
            elif self.db == 'mysql':
                pass
            else:
                pass

        content = self.ids.scrn_product_contents
        content.clear_widgets()

        if self.db == 'mongo':
            # MongoDB
            self.stocks.remove({'product_code':code})
            products = self.mongo_get_products()
        elif self.db == 'mysql':
            # MySQL
            sql = "DELETE FROM stocks WHERE product_code=%s"
            values = [code]
            self.mycursor.execute(sql, values)
            self.mydb.commit()
            products = self.mysql_get_products()
        else:
            pass
        
        productstable = DataTable(table=products)
        content.add_widget(productstable)

    def view_stats(self):
        plt.cla()
        self.ids.analysis_res.clear_widgets()
        
        target_product = self.ids.target_products.text
        code, name = target_product.split(' | ')

        df = pd.read_csv('products_purchase.csv')
        purchases = []
        dates = []
        count = 0
        for i in range(len(df)):
            if str(df.Product_Code[i]) == code:
                purchases.append(df.Purchased[i])
                dates.append(count)
                count += 1
        plt.bar(dates,purchases,color='teal',label=name)
        plt.ylabel('Total Purchases')
        plt.xlabel('day')

        self.ids.analysis_res.add_widget(FCK(plt.gcf()))


class AdminApp(App):
    def build(self):
        return AdminWindow(db='mongo')


if __name__ == "__main__":
    aa = AdminApp()
    aa.run()