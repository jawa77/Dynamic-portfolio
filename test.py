from alexapy import Alexa

# Initialize the Alexa object
alexa = Alexa(email="anonymous002k2@gmail.com", password="jawa@2002")

# Authenticate
alexa.authenticate()

# Make the announcement on all your Echo devices
alexa.send_announcement("I am Rahul")
