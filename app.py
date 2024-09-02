from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017')

db = client['contact_db']
users_collection = db['users']
contacts_collection = db['contacts']


from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017')

db = client['contact_db']
users_collection = db['users']
contacts_collection = db['contacts']


@app.route('/register_A_User', methods=['POST'])
def register_As_A_User():
    data = request.get_json()

    if not data.get('firstName') or data['firstName'].strip() == "":
        return jsonify({'error': "firstName is empty, please enter firstName"}), 400

    if not data.get('lastName') or data['lastName'].strip() == '':
        return jsonify({'error': "lastName is empty, please enter lastName"}), 400

    phone_number = data.get('phoneNumber')
    if not phone_number or phone_number.strip() == '':
        return jsonify({'error': "phoneNumber is empty, please enter a phoneNumber"}), 400

    if not phone_number.isdigit() or len(phone_number) != 11:
        return jsonify({'error': "phone number must be 11 digits and non-negative"}), 400

    if not data.get('registrationPassword') or data['registrationPassword'].strip() == '':
        return jsonify({'error': "registrationPassword is empty, please input a password"}), 400

    if not data.get('confirmPassword') or data['confirmPassword'].strip() == '':
        return jsonify({'error': "confirmPassword is empty, please enter a confirm Password"}), 400

    if not data.get('userName') or data['userName'].strip() == '':
        return jsonify({'error': "userName is empty, please enter a userName"}), 400

    if not data.get('email') or data['email'].strip() == '':
        return jsonify({'error': "email is empty, please enter an email"}), 400

    if not data.get('address') or data['address'].strip() == '':
        return jsonify({'error': "home address is empty, please enter your home address"}), 400

    duplicate_userName = users_collection.find_one({'userName': data['userName']})
    if duplicate_userName:
        return jsonify({'error': 'A user with this username already exists'}), 400

    duplicate_password = users_collection.find_one({"registrationPassword": data["registrationPassword"]})
    if duplicate_password:
        return jsonify({'error': "password already exists"}), 400

    new_user = {
        'firstName': data['firstName'],
        'lastName': data['lastName'],
        'phoneNumber': data['phoneNumber'],
        'email': data['email'],
        'address': data['address'],
        'userName': data['userName'],
        'registrationPassword': data['registrationPassword']
    }
    users_collection.insert_one(new_user)

    response = {
        'firstName': new_user['firstName'],
        'lastName': new_user['lastName'],
        'userName': new_user['userName'],
        'phoneNumber': new_user['phoneNumber'],
        'email': new_user['email'],
        'message': "You have successfully registered as a new user"
    }
    return jsonify(response), 201


@app.route('/userLogin', methods=['post'])
def user_Login():
    login = request.get_json()
    print("Received login data:", login)

    if not login.get('userName') or login['userName'].strip() == '':
        return jsonify({'message': "userName is empty, please input userName"}), 400

    if not login.get('password') or login['password'].strip() == "":
        return jsonify({'message': "password is empty, please input a password"}), 400

    user = users_collection.find_one({'userName': login['userName']})
    print("Retrieved user data:", user)

    if not user:
        return jsonify({'message': "user not found, please register first"}), 400

    if user['registrationPassword'] != login['password']:
        return jsonify({'message': "password does not match with your registration password"}), 400

    return jsonify({'message': "Login successful"}), 200


@app.route('/createContact', methods=['POST'])
def create_contact():
    data = request.get_json()
    print("received request", data)

    if not data.get('firstName'):
        return jsonify({"error": "firstName is empty pls enter firstName"}), 400

    if not data.get('lastName'):
        return jsonify({"error": "lastName is empty pls enter lastName"}), 400

    if not data.get('phoneNumber'):
        return jsonify({"error": "phoneNumber is empty pls input a phoneNumber"}), 400

    if not data.get('email'):
        return jsonify({"error": "email is empty enter an email"}), 400

    if len(data.get("phoneNumber")) != 11:
        return jsonify({"error": "phone number must be up to 11 digits"}), 400

    duplicate_contact_names = contacts_collection.find_one({
        "firstName": data['firstName'],
        "lastName": data['lastName']
    })
    if duplicate_contact_names:
        return jsonify(
            {"error": f"A contact already exists with firstName {data['firstName']} and lastName {data['lastName']}"}
        ), 400

    new_contact = {
        'firstName': data['firstName'],
        'lastName': data['lastName'],
        'phoneNumber': data['phoneNumber'],
        'email': data['email'],
    }
    contacts_collection.insert_one(new_contact)
    response = {
        'firstName': new_contact['firstName'],
        'lastName': new_contact['lastName'],
        'phoneNumber': new_contact['phoneNumber'],
        'email': new_contact['email'],
        'message': "You have created a new contact"
    }
    print("response", response)
    return jsonify(response), 200


@app.route('/edit_User_Contact', methods=['PUT'])
def edit_User_Contact():
    data = request.get_json()
    print("received request", data)
    user_with_phoneNumber = contacts_collection.find_one({
        'phoneNumber': data['phoneNumber']
    })
    if not user_with_phoneNumber:
        return jsonify({'error': 'user with the phoneNumber does not exist'}), 404
    updated_data = {}
    if 'firstName' in data:
        updated_data['firstName'] = data['firstName']
    if 'lastName' in data:
        updated_data['lastName'] = data['lastName']
    if 'phoneNumber' in data:
        updated_data['phoneNumber'] = data['phoneNumber']

    contacts_collection.update_one(
        {'phoneNumber': data['phoneNumber']},
        {'$set': updated_data}
    )
    print("updated data", updated_data)

    return jsonify({'message': 'Contact updated successfully'})


@app.route('/find_Contact_By_Email', methods=['GET'])
def find_Contact_By_Email():
    try:
        email = request.args.get('email')
        print("Received request with email:", email)

        if not email:
            print("Error: Email is required")
            return jsonify({'error': 'Email is required'}), 400

        print("Searching in contacts_collection for email:", email)

        user_contact_by_email = contacts_collection.find_one({'email': email})

        if not user_contact_by_email:
            print("Error: User with email not found")
            return jsonify({'error': 'User with email not found'}), 404

        user_contact_by_email['_id'] = str(user_contact_by_email['_id'])

        response = {
            "message": "User contact found with email",
            "contact": user_contact_by_email
        }
        print("Response outcome:", response)
        return jsonify(response), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/delete_Contact_By_User', methods=['DELETE'])
def delete_Contact_By_User():
    data = request.get_json()
    print("requested data", data)
    if not data or 'phoneNumber' not in data:
        return jsonify({'error': 'Phone number is required'})

    user_delete = contacts_collection.find_one({'phoneNumber': data['phoneNumber']})

    if not user_delete:
        return jsonify({'error': "User you want to delete is not found with the phone number you provided"}), 404

    contacts_collection.delete_one({'phoneNumber': data['phoneNumber']})
    print("deleted data", user_delete)
    return jsonify({'message': 'User deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)

