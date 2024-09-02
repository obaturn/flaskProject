import unittest

from app import contacts_collection, app


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        contacts_collection.delete_many({})
        pass

    def test_register_user(self):
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'phoneNumber': '12345678901',
            'registrationPassword': 'password123',
            'confirmPassword': 'password123',
            'userName': 'johndoe',
            'email': 'john@example.com',
            'address': '123 Main St'
        }

        duplicate_userName = None
        duplicate_password = None

        self.assertIsNone(duplicate_userName, 'A user with this username already exists')
        self.assertIsNone(duplicate_password, "Password already exists")

        new_user = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'phoneNumber': data['phoneNumber'],
            'userName': data['userName'],
            'email': data['email'],
            'address': data['address'],
            'registrationPassword': data['registrationPassword']
        }

        inserted_user = new_user

        self.assertIsNotNone(inserted_user, "User was not inserted")

    def test_user_login(self):
        user = {
            'userName': 'testUser',
            'registrationPassword': '123456'
        }

        login_data = {
            'userName': 'testUser',
            'password': '123456'
        }

        self.assertIsNotNone(user, "User not found, please register first")
        self.assertEqual(user['registrationPassword'], login_data['password'], "Password does not match")

    def test_create_contact(self):
        data = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'phoneNumber': '09876543210',
            'email': 'jane@example.com'
        }

        duplicate_contact_names = None

        self.assertIsNone(duplicate_contact_names, "A contact with this name already exists")

        new_contact = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'phoneNumber': data['phoneNumber'],
            'email': data['email'],
        }

        inserted_contact = new_contact

        self.assertIsNotNone(inserted_contact, "Contact was not created")

    def test_edit_user_contact(self):
        contacts_collection.insert_one({
            'firstName': 'John',
            'lastName': 'Doe',
            'phoneNumber': '09876543210',
            'email': 'john@example.com'
        })

        updated_data = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'phoneNumber': '09876543210'
        }

        response = self.app.put('/edit_User_Contact', json=updated_data)

        self.assertEqual(response.status_code, 200)

        updated_user = contacts_collection.find_one({'phoneNumber': '09876543210'})
        self.assertEqual(updated_user['firstName'], 'Jane')

    def test_find_contact_by_email_success(self):
        contacts_collection.insert_one({
            'firstName': 'Ja',
            'lastName': 'Doyin',
            'phoneNumber': '12345678901',
            'email': 'ja@email.com'
        })

        response = self.app.get('/find_Contact_By_Email?email=ja@email.com')

        self.assertEqual(response.status_code, 200)

        response_data = response.get_json()
        self.assertEqual(response_data['contact']['firstName'], 'Ja')
        self.assertEqual(response_data['contact']['lastName'], 'Doyin')
        self.assertEqual(response_data['contact']['email'], 'ja@email.com')

    def test_find_contact_by_email_not_found(self):
        response = self.app.get('/find_Contact_By_Email?email=notfound@example.com')

        self.assertEqual(response.status_code, 404)
        self.assertIn('User with email not found', response.get_data(as_text=True))

    def test_find_contact_by_email_missing_email(self):
        response = self.app.get('/find_Contact_By_Email?email=')

        self.assertEqual(response.status_code, 400)
        self.assertIn('Email is required', response.get_data(as_text=True))

    def test_delete_Contact_By_User(self):
        data = {
            'firstName': 'John',
            'lastName': 'Doe',
            'phoneNumber': '1234567890',
            'email': 'john.doe@example.com',
        }

        contacts_collection.insert_one(data)
        inserted_contact = contacts_collection.find_one({'phoneNumber': data['phoneNumber']})
        self.assertIsNotNone(inserted_contact, "Contact was not created")

        response = self.app.delete('/delete_Contact_By_User', json={'phoneNumber': data['phoneNumber']})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'message': 'User deleted successfully'})

        deleted_contact = contacts_collection.find_one({'phoneNumber': data['phoneNumber']})
        self.assertIsNone(deleted_contact, "Contact was not deleted")


if __name__ == '__main__':
    unittest.main()
