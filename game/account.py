#!/usr/bin/env python3.5
'''
This module acts as a handler for logins, account creation, and account management.
'''
import re
import bcrypt

def login(client):
    usrchk_running = True
    pwdchk_running = True

    while usrchk_running:
        client.server.broadcast("Please enter your username: ", client.client, client.name)
        username = client.receiveData()
        pattern = r"" + username
        if [key for key, value in client.server.users.items() if re.search(pattern, key)]:
            while pwdchk_running:
                client.server.broadcast("Password: ", client.client, client.name)
                password = client.receiveData()
                if bcrypt.checkpw(password, client.server.users[username]):
                    self.server.message("Login successful. Welcome to the server.\n", client.client, client.name)
                    usrchk_running = False
                    pwdchk_running = False
                else:
                    client.server.broadcast("Password incorrect.", client.client, client.name)
        else:
            createUser(client, username)


def createUser(client, username):
    client.server.broadcast("This user does not exists. Create new user? (y/n)", client.client, client.name)
    creatingUser = True

    while creatingUser:
        print("In creating user loop")
        data = client.receiveData()
        if data == 'y':
            print("answer was y")
            client.server.broadcast("Creating new user with username '" + username + "'. \nEnter your new password: ", client.client, client.name)
            password = bcrypt.hashpw(client.receiveData().encode(), bcrypt.gensalt())
            if password:
                print("password has been entered")
                client.server.users[username] = password
                client.server.broadcast("User created. Returning to login prompt...", client.client, client.name)
                client.server.saveUsers()
                creatingUser = False
            elif data == 'n':
                print("answer was n")
                client.server.broadcast("New user creation declined. Returning to login prompt.", client.client, client.name)
                creatingUser = False
            else:
                print("answer was invalid")
                client.server.broadcast("Input invalid. You must use 'y' or 'n'.", client.client, client.name)


    
