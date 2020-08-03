from flask import Flask, jsonify, request
import sqlfile as SqlFile
app = Flask(__name__)

@app.route('/', methods=['GET'])
def test():
    return jsonify({'message' : 'It works'})

@app.route('/getUser', methods=['POST'])
def login():
    data_tuple = (request.json['user_email'], request.json['user_password'])
    result = SqlFile.userLogin(data_tuple)
    if result == []:
        return jsonify({ 'Status' :  404, 'Message' : 'User is not found'}), 404
    else:
        resultRole = SqlFile.userGetRole(data_tuple)
        if resultRole != []:
            result[0].update({'role': resultRole[0]})
        else:
            result[0].update({'role': None})
        
        resultOrganization = SqlFile.userGetOrganization(data_tuple)
        if resultOrganization != []:
            result[0].update({'organization': resultOrganization[0]})
        else:
            result[0].update({'organization': None})
        
        return jsonify(result[0]), 200
        
@app.route('/signup', methods=['POST'])
def signup():
    insert_data_tuple = (request.json['user_name'], request.json['user_surname'], request.json['user_email'], request.json['user_password'], request.json['user_gender'], request.json['user_image'])
    select_data_tuple = (request.json['user_email'])
    result = SqlFile.userSignUpSearch(select_data_tuple)
    if result != []:
        return jsonify({ 'Status' :  302, 'Message' : 'Same user is occured'}),302
    else:
        SqlFile.userSignUpInsert(insert_data_tuple)
        return jsonify({ 'Status' :  200, 'Message' : 'User is inserted succesfully'}),200

@app.route('/organizationjoin', methods=['POST'])
def organizationJoin():
    update_data_tuple = (request.json['organization_id'], request.json['user_id'])
    role_update_data_tuple = (2, request.json['user_id'])
    search_data_tuple = (request.json['organization_id'])
    result = SqlFile.organizationSearchSelect(search_data_tuple)
    if result == []:
        return jsonify({ 'Status' :  404, 'Message' : 'Organization is not found'}), 404
    else:
        SqlFile.organizationJoinUpdate(update_data_tuple)
        SqlFile.userRoleUpdate(role_update_data_tuple)
        return jsonify({ 'Status' :  200, 'Message' : 'User join in organization succesfuly'}), 200

@app.route('/organizationcreate', methods=['POST'])
def organizationCreate():
    data_tuple = (request.json['organization_name'], request.json['organization_industry'], request.json['organization_image'])
    SqlFile.organizationCreateInsert(data_tuple)
    # user role update
    role_update_data_tuple = (1, request.json['user_id'])
    SqlFile.userRoleUpdate(role_update_data_tuple)
    # user organization id update
    result_getOrganizationID = SqlFile.organizationGetOrganizationID()
    organization_id = result_getOrganizationID[0]['organization_id']
    update_data_tuple = (organization_id, request.json['user_id'])
    SqlFile.organizationJoinUpdate(update_data_tuple)
    return jsonify({ 'Status' :  200, 'Message' : 'Organization is created succesfully'}), 200

@app.route('/userinformationupdate', methods=['POST'])
def userProfileUpdate():
    data_tuple = (request.json['user_image'], request.json['user_name'], request.json['user_surname'], request.json['user_id'])
    SqlFile.userInformationUpdate(data_tuple)
    return jsonify({ 'Status' :  200, 'Message' : 'User informations are updated succesfully'}), 200

@app.route('/userchangepassword', methods=['POST'])
def userChangePassword():
    data_tuple = (request.json['user_password_change_with'], request.json['user_id'])
    pass_control_tuple = (request.json['user_id'], request.json['user_password'])
    result_control = SqlFile.userPasswornControl(pass_control_tuple)
    if result_control == []:
        return jsonify({ 'Status' :  404, 'Message' : 'User password is not same'}), 404
    else:
        SqlFile.userPasswordChange(data_tuple)
        return jsonify({ 'Status' :  200, 'Message' : 'User password is updated succesfully'}), 200

@app.route('/listallproduct', methods=['POST'])
def listAllProduct():
    data_tuple = (request.json['organization_id'])
    result = SqlFile.listAllProductCall(data_tuple) 
    return jsonify(result), 200

@app.route('/createnewproduct', methods=['POST'])
def ceateNewProduct():
    data_tuple = (request.json['product_name'], request.json['product_serial'], request.json['product_brand'], request.json['product_purchase_price'], request.json['product_sales_price'], request.json['product_description'], request.json['product_image'])
    SqlFile.productCreateInsert(data_tuple) 
    # create new inventory
    result_getProductID = SqlFile.productGetProductID()
    product_id = result_getProductID[0]['product_id']
    create_inventory_tuple = (request.json['organization_id'], product_id)
    SqlFile.productCreateInventoryInsert(create_inventory_tuple)
    return jsonify({ 'Status' :  200, 'Message' : 'Product is created succesfully'}), 200

@app.route('/updateproduct', methods=['POST'])
def updateProduct():
    data_tuple = (request.json['product_name'], request.json['product_serial'], request.json['product_brand'], request.json['product_purchase_price'], request.json['product_sales_price'], request.json['product_description'], request.json['product_image'], request.json['product_id'])
    SqlFile.productInformationUpdate(data_tuple) 
    return jsonify({ 'Status' :  200, 'Message' : 'Product is updated succesfully'}), 200

@app.route('/searchproduct', methods=['POST'])
def getProduct():
    data_tuple = (request.json['organization_id'], request.json['product_serial'])
    result = SqlFile.getOneProductCall(data_tuple)
    if result != []:
        return jsonify(result[0]), 200
    else:
        return jsonify({ 'Status' :  404, 'Message' : 'Product is not found'}), 404

@app.route('/placeOrder', methods=['POST'])
def burOrSellProduct():
    is_sale = request.json['order_is_sales']
    product_list = request.json['product_list']

    if is_sale == 1:
        for product in product_list:
            print(product['product_id'])
            print(product['orderline_quantity'])
            product_id = product['product_id']
            orderline_quantity = product['orderline_quantity']
            orderline_unit_price_result = SqlFile.orderGetOrderSalesPrice((product_id))
            orderline_unit_price = orderline_unit_price_result[0]['product_sales_price']
            inventory_quantity_result = SqlFile.productGetProductInventoryQuantity((request.json['organization_id'], product_id))
            inventory_quantity = inventory_quantity_result[0]['inventory_quantity']
            new_inventory_quantity = inventory_quantity - orderline_quantity
            if new_inventory_quantity < 0:
                product_name_result = SqlFile.orderGetOrderProductName((product_id))
                product_name = product_name_result[0]['product_name']
                Message = 'Quantity of product named '+str(product_name)+' is not enough to sale. Its quantity is '+str(inventory_quantity)+' rigth now.'
                return jsonify({ 'Status' :  404, 'Message' : Message}), 404
            # create new Order
            order_data_tuple = (request.json['order_is_sales'], request.json['organization_id'], request.json['user_id'])
            SqlFile.orderCreateNewInsert(order_data_tuple)
            # get last order ID
            result_getOrderID = SqlFile.orderGetOrderID()
            order_id = result_getOrderID[0]['order_id']
            # create new orderline
            SqlFile.inventoryInformationUpdate((new_inventory_quantity, request.json['organization_id'], product_id))
            SqlFile.orderLineCreateNewInsert((product_id, order_id, orderline_quantity, orderline_unit_price))
        
        return jsonify({ 'Status' :  200, 'Message' : 'Sale is completed successfully'}), 200
    else:
        for product in product_list:
            print(product['product_id'])
            print(product['orderline_quantity'])
            product_id = product['product_id']
            orderline_quantity = product['orderline_quantity']
            orderline_unit_price_result = SqlFile.orderGetOrderPurchasePrice((product_id))
            orderline_unit_price = orderline_unit_price_result[0]['product_purchase_price']
            inventory_quantity_result = SqlFile.productGetProductInventoryQuantity((request.json['organization_id'], product_id))
            inventory_quantity = inventory_quantity_result[0]['inventory_quantity']
            new_inventory_quantity = inventory_quantity + orderline_quantity
            # create new Order
            order_data_tuple = (request.json['order_is_sales'], request.json['organization_id'], request.json['user_id'])
            SqlFile.orderCreateNewInsert(order_data_tuple)
            # get last order ID
            result_getOrderID = SqlFile.orderGetOrderID()
            order_id = result_getOrderID[0]['order_id']
            # create new orderline
            SqlFile.inventoryInformationUpdate((new_inventory_quantity, request.json['organization_id'], product_id))
            SqlFile.orderLineCreateNewInsert((product_id, order_id, orderline_quantity, orderline_unit_price))
        
        return jsonify({ 'Status' :  200, 'Message' : 'Purchase is completed successfully'}), 200

@app.route('/getOrderReport', methods=['POST'])
def getOrderReport():
    data_tuple = ( request.json['order_is_sales'], request.json['organization_id'])
    order_result = SqlFile.orderBuyOrSellReport(data_tuple)
    if order_result == []:
        return jsonify({ 'Status' :  404, 'Message' : 'There is no report'}), 404
    else:
        countOfOrder = len(order_result)

        for i in range(countOfOrder):
            order_line_list = SqlFile.orderGetOrderLineReport((order_result[i]['order_id']))
            countOfOrderLine = len(order_line_list)
            total_order = 0
            for j in range(countOfOrderLine):
                total_order = total_order + order_line_list[j]['total_price']
            order_result[i].update({'total_order': total_order})
            order_result[i].update({'order_line_list': order_line_list})

        return jsonify(order_result), 200

@app.route('/updateorganization', methods=['POST'])
def updateOrganization():
    data_tuple = (request.json['organization_name'], request.json['organization_industry'], request.json['organization_image'], request.json['organization_id'])
    SqlFile.organizationInformationUpdate(data_tuple)
    return jsonify({ 'Status' :  200, 'Message' : 'Organization is updated succesfully'}), 200

@app.route('/getorgusers', methods=['POST'])
def getUsersForManagement():
    data_tuple = (request.json['organization_id'])
    user_result = SqlFile.managementGetUser(data_tuple)
    user_role_result = SqlFile.managementGetUserRole(data_tuple)

    countOfUser = len(user_result)

    for i in range(countOfUser):
        role_result = SqlFile.managementGetUserRoleInformation((user_role_result[i]['role_id']))
        user_result[i].update({'role': role_result[0]})

    return jsonify(user_result), 200

@app.route('/getRoles', methods=['GET'])
def getRoles():
    return jsonify(SqlFile.getRoleQuerty()), 200

@app.route('/setUserRole', methods=['POST'])
def setUserRole():
    data_tuple = (request.json['role_id'] ,request.json['user_id'])
    SqlFile.setUserRoleQuery(data_tuple)
    return jsonify({ 'Status' :  200, 'Message' : 'User role is updated succesfully'}), 200

@app.route('/removeUserFromOrg', methods=['POST'])
def removeUserFromOrg():
    data_tuple = (request.json['user_id'])
    SqlFile.removeUserFromOrgQuery(data_tuple)
    return jsonify({ 'Status' :  200, 'Message' : 'User is delated from organization succesfully'}), 200

@app.route('/getProductById', methods=['POST'])
def getProductById():
    data_tuple = (request.json['product_id'])
    result = SqlFile.getProductByIdQuery(data_tuple)
    if result != []:
        return jsonify(result[0]), 200
    else:
        return jsonify({ 'Status' :  404, 'Message' : 'Product is not found.'}), 404

if __name__ == "__main__":
    app.run(debug=True)