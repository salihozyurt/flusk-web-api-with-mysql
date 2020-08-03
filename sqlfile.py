import mysql.connector
from mysql.connector import Error
import json

def dbConnection():
    connection = mysql.connector.connect(host="flasktest.cz00tn1p6lg1.us-east-2.rds.amazonaws.com", 
                                        database="storemation", 
                                        user="admin", 
                                        passwd="password", 
                                        auth_plugin='mysql_native_password')
    return connection

def executeQuery(query, data_tuple):
    try:
        connection = dbConnection()

        print(connection)

        if(connection):
            print("Succesful")
        else:
            print("Unsuccesful")
        
        if(data_tuple==()):
            cursor = connection.cursor()
            cursor.execute(query)
        else:
            cursor = connection.cursor(prepared=True)
            cursor.execute(query, data_tuple)

        row_headers = [x[0] for x in cursor.description]
        records = cursor.fetchall()
        print("Total number of rows in Student is: ", cursor.rowcount)

        print("\nPrinting each student record")
        payload=[]
        for row in records:
            payload.append(dict(zip(row_headers,row)))
        print(payload)
        cursor.close()
        return payload
        
    except Error as e:
        print("Error reading data from MySQL table", e)
    

def executeNonQuery(query, data_tuple):
    try:
        connection = dbConnection()

        print(connection)

        if(connection):
            print("Succesful")
        else:
            print("Unsuccesful")
        
        if(data_tuple==()):
            return {'message' : 'Non-exists any value'}
        else:
            cursor = connection.cursor(prepared=True)
            cursor.execute(query, data_tuple)
            connection.commit()
            cursor.close()
            return {'message' : 'Success'}
            
    except Error as e:
        print("Error reading data from MySQL table", e)
        return {'message' : e}

# user login sql query
def userLogin(data_tuple):
    return executeQuery("""SELECT user_id, user_name, user_surname, user_email, user_password, user_gender, user_image FROM user_table WHERE user_email = %s AND user_password = %s""", data_tuple)

# user get role sql query
def userGetRole(data_tuple):
    return executeQuery("""SELECT * FROM role_table WHERE role_id = (SELECT role_id FROM user_table WHERE user_email = %s AND user_password = %s)""", data_tuple)

# user get role sql query
def userGetOrganization(data_tuple):
    return executeQuery("""SELECT * FROM organization_table WHERE organization_id = (SELECT organization_id FROM user_table WHERE user_email = %s AND user_password = %s)""", data_tuple)

# user sign up sql search query we control same user is occur
def userSignUpSearch(data_tuple):
    return executeQuery("""SELECT * FROM user_table WHERE user_email = %s""", (data_tuple,))

# user sign up sql insert query we store database user informations
def userSignUpInsert(data_tuple):
    return executeNonQuery("""INSERT INTO user_table(user_name, user_surname, user_email, user_password, user_gender, user_image) VALUES (%s, %s, %s, %s, %s, %s)""", data_tuple)

# organization search
def organizationSearchSelect(data_tuple):
    return executeQuery("""SELECT * FROM organization_table WHERE organization_id = %s""", (data_tuple,))

# user join organization sql query
def organizationJoinUpdate(data_tuple):
    return executeNonQuery("""UPDATE user_table SET organization_id = %s WHERE user_id=%s""", data_tuple)

# user join organization sql query
def userRoleUpdate(data_tuple):
    return executeNonQuery("""UPDATE user_table SET role_id = %s WHERE user_id=%s""", data_tuple)

# user organization create sql insert query
def organizationCreateInsert(data_tuple):
    return executeNonQuery("""INSERT INTO organization_table(organization_name, organization_industry, organization_image) values (%s, %s, %s)""", data_tuple)

# organization search
def organizationGetOrganizationID():
    return executeQuery("""SELECT organization_id FROM organization_table ORDER BY organization_id DESC LIMIT 1""", ())

# user profile update sql query
def userInformationUpdate(data_tuple):
    return executeNonQuery("""UPDATE user_table SET user_image = %s, user_name = %s, user_surname = %s WHERE user_id=%s""", data_tuple)

# user password control sql query
def userPasswornControl(data_tuple):
    return executeQuery("""SELECT user_password FROM user_table WHERE user_id = %s AND user_password = %s""", data_tuple)

# user password update sql query
def userPasswordChange(data_tuple):
    return executeNonQuery("""UPDATE user_table SET user_password = %s WHERE user_id=%s""", data_tuple)

# list all product for organization id
def listAllProductCall(data_tuple):
    return executeQuery("""SELECT P.product_id, P.product_name, P.product_serial, P.product_brand, TRUNCATE(P.product_purchase_price,2) AS product_purchase_price, TRUNCATE(P.product_sales_price,2) AS product_sales_price, P.product_description, P.product_image, I.inventory_quantity FROM product_table AS P, inventory_table AS I, organization_table AS O WHERE I.organization_id = O.organization_id AND I.product_id = P.product_id AND I.organization_id = %s""", (data_tuple,))

# create new product
def productCreateInsert(data_tuple):
    return executeNonQuery("""INSERT INTO product_table(product_name, product_serial, product_brand, product_purchase_price, product_sales_price, product_description, product_image) values (%s,%s,%s,%s,%s,%s,%s)""", data_tuple)

# get last product id
def productGetProductID():
    return executeQuery("""SELECT product_id FROM product_table ORDER BY product_id DESC LIMIT 1""", ())

# create new inventory
def productCreateInventoryInsert(data_tuple):
    return executeNonQuery("""INSERT INTO inventory_table(organization_id, product_id, inventory_quantity) values (%s,%s,0)""", data_tuple)

# product update sql query
def productInformationUpdate(data_tuple):
    return executeNonQuery("""UPDATE product_table SET product_name = %s, product_serial = %s, product_brand = %s, product_purchase_price = %s, product_sales_price = %s, product_description = %s, product_image = %s WHERE product_id=%s""", data_tuple)

# inventory update sql query
def inventoryInformationUpdate(data_tuple):
    return executeNonQuery("""UPDATE inventory_table SET inventory_quantity = %s WHERE organization_id=%s AND product_id=%s""", data_tuple)

# getProduct sql query
def getOneProductCall(data_tuple):
    return executeQuery("""SELECT P.product_id, P.product_name, P.product_serial, P.product_brand, TRUNCATE(P.product_purchase_price,2) AS product_purchase_price, TRUNCATE(P.product_sales_price,2) AS product_sales_price, P.product_description, P.product_image, I.inventory_quantity FROM product_table AS P, inventory_table AS I, organization_table AS O WHERE I.organization_id = O.organization_id AND I.product_id = P.product_id AND I.organization_id = %s AND P.product_serial = %s""", data_tuple)

# create order
def orderCreateNewInsert(data_tuple):
    return executeNonQuery("""INSERT INTO order_table(order_date, order_is_sale, organization_id, user_id) values (sysdate(),%s,%s,%s)""", data_tuple)

# get last order id
def orderGetOrderID():
    return executeQuery("""SELECT order_id FROM order_table ORDER BY order_id DESC LIMIT 1""", ())

# get product sales price
def orderGetOrderSalesPrice(data_tuple):
    return executeQuery("""SELECT product_sales_price FROM product_table WHERE product_id = %s""", (data_tuple,))

# get product purchase price
def orderGetOrderPurchasePrice(data_tuple):
    return executeQuery("""SELECT product_purchase_price FROM product_table WHERE product_id = %s""", (data_tuple,))

# get product name
def orderGetOrderProductName(data_tuple):
    return executeQuery("""SELECT product_name FROM product_table WHERE product_id = %s""", (data_tuple,))

# get product inventory quantity
def productGetProductInventoryQuantity(data_tuple):
    return executeQuery("""SELECT I.inventory_quantity FROM product_table AS P, inventory_table AS I, organization_table AS O WHERE I.organization_id = O.organization_id AND I.product_id = P.product_id AND I.organization_id = %s AND P.product_id = %s""", data_tuple)

# create order line
def orderLineCreateNewInsert(data_tuple):
    return executeNonQuery("""INSERT INTO orderline_table(product_id, order_id, orderline_quantity, orderline_unit_price) values (%s,%s,%s,%s)""", data_tuple)

# get order information 
def orderBuyOrSellReport(data_tuple):
    return executeQuery("""SELECT O.order_id, DATE_FORMAT(O.order_date, '%d.%m.%Y') AS order_date, CONCAT(CONCAT(U.user_name, ' '), U.user_surname) AS fullname  FROM user_table AS U, order_table AS O WHERE O.user_id = U.user_id AND O.order_is_sale = %s AND O.organization_id = %s""", data_tuple)

# get order orderline information
def orderGetOrderLineReport(data_tuple):
    return executeQuery("""SELECT P.product_id, P.product_name, P.product_brand, O.orderline_quantity, TRUNCATE(O.orderline_unit_price,2) AS orderline_unit_price , TRUNCATE(orderline_quantity*orderline_unit_price,2) AS total_price FROM orderline_table AS O, product_table AS P WHERE O.product_id = P.product_id AND O.order_id = %s""", (data_tuple,))

# get order user id information
def orderBuyOrSellReportUserId(data_tuple):
    return executeQuery("""SELECT user_id FROM order_table WHERE organization_id = %s AND order_is_sale = %s""", data_tuple)

# get order user all information
def orderGetUserInformation(data_tuple):
    return executeQuery("""SELECT user_id, user_name, user_surname, user_email, user_gender  FROM user_table WHERE user_id = %s""", (data_tuple,))

# get order orderline information
def orderGetOrderLineInformation(data_tuple):
    return executeQuery("""SELECT orderline_quantity, orderline_unit_price FROM orderline_table WHERE order_id = %s""", (data_tuple,))

# get order orderline product id
def orderGetOrderLineProductId(data_tuple):
    return executeQuery("""SELECT product_id FROM orderline_table WHERE order_id = %s""", (data_tuple,))

# get order orderline product information
def orderGetOrderLineProductInformation(data_tuple):
    return executeQuery("""SELECT * FROM product_table WHERE product_id = %s""", (data_tuple,))

# organization update sql query
def organizationInformationUpdate(data_tuple):
    return executeNonQuery("""UPDATE organization_table SET organization_name = %s, organization_industry = %s, organization_image = %s WHERE organization_id=%s""", data_tuple)

# user information of management sql query
def managementGetUser(data_tuple):
    return executeQuery("""SELECT user_id, user_name, user_surname, user_email, user_password, user_gender, user_image FROM user_table WHERE organization_id = %s""", (data_tuple,))

# user role information of management sql query
def managementGetUserRole(data_tuple):
    return executeQuery("""SELECT role_id FROM user_table WHERE organization_id = %s""", (data_tuple,))

# user role information of management sql query
def managementGetUserRoleInformation(data_tuple):
    return executeQuery("""SELECT * FROM role_table WHERE role_id = %s""", (data_tuple,))

# getRoles SQL Query
def getRoleQuerty():
    return executeQuery("""SELECT * FROM role_table""", ())

# setUserRoleQuery SQL Query
def setUserRoleQuery(data_tuple):
    return executeNonQuery("""UPDATE user_table SET role_id = %s WHERE user_id=%s""", data_tuple)

# organization update sql query
def removeUserFromOrgQuery(data_tuple):
    return executeNonQuery("""UPDATE user_table SET role_id = null, organization_id = null WHERE user_id=%s""", (data_tuple,))

# getProductById sql query
def getProductByIdQuery(data_tuple):
    return executeQuery("""SELECT product_id, product_name, product_serial, product_brand, TRUNCATE(product_purchase_price,2) AS product_purchase_price, TRUNCATE(product_sales_price,2) AS product_sales_price, product_description, product_image FROM product_table WHERE product_id = %s""", (data_tuple,))

# finito
# 