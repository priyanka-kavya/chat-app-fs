import unittest
import socketio

# Import your app and relevant modules here
from app import create_app, socketio, users, groups

class TestChatAppFunctionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a SocketIO client for testing
        cls.client = socketio.Client()

        # Start the SocketIO server
        cls.server = create_app().test_client()

        # Connect the client to the server
        cls.client.connect('http://localhost:5000')

    @classmethod
    def tearDownClass(cls):
        # Disconnect the client and stop the server
        cls.client.disconnect()
        socketio.server.stop()

    def test_create_user(self):
        # Emit a create_user event
        self.client.emit('create_user', {'username': 'new_user', 'password': 'new_password'})

        # Assert that the user is created
        self.assertIsNotNone(users.get('new_user'))

    def test_edit_user(self):
        # Emit an edit_user event
        self.client.emit('edit_user', {'username': 'new_user', 'password': 'new_password_updated'})

        # Assert that the user's password is updated
        user = users.get('new_user')
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('new_password_updated'))

    def test_create_group(self):
        # Emit a create_group event
        self.client.emit('create_group', {'group_name': 'new_group'})

        # Assert that the group is created
        self.assertIsNotNone(groups.get('new_group'))

    def test_delete_group(self):
        # Emit a delete_group event
        self.client.emit('delete_group', {'group_name': 'existing_group'})

        # Assert that the group is deleted
        self.assertIsNone(groups.get('existing_group'))

    def test_add_user_to_group(self):
        # Emit an add_user_to_group event
        self.client.emit('add_user_to_group', {'username': 'existing_user', 'group_name': 'existing_group'})

        # Assert that the user is added to the group
        group = groups.get('existing_group')
        self.assertIsNotNone(group)
        self.assertIn('existing_user', group.members)

    def test_remove_user_from_group(self):
        # Emit a remove_user_from_group event
        self.client.emit('remove_user_from_group', {'username': 'existing_user', 'group_name': 'existing_group'})

        # Assert that the user is removed from the group
        group = groups.get('existing_group')
        self.assertIsNotNone(group)
        self.assertNotIn('existing_user', group.members)

    def test_send_group_message(self):
        # Simulate joining a group
        self.client.emit('join_group', {'username': 'test_user', 'group_name': 'test_group'})
        self.client.on('message', self.on_message)  # Set up a message handler

        # Emit a send_group_message event
        self.client.emit('send_group_message', {'username': 'test_user', 'group_name': 'test_group', 'message': 'Hello, group!'})

        # Wait for the server's response (you can use a timeout if needed)
        self.client.sleep(1)

    def on_message(self, data):
        # Handle the message received from the server
        self.assertEqual(data, 'test_user: Hello, group!')

if __name__ == '__main__':
    unittest.main()
