from bcrypt import checkpw, gensalt, hashpw

def hash_pass(password):
    return hashpw(password.encode('utf8'), gensalt())

def verify_pass(provided_password, stored_password):
    return checkpw(provided_password.encode('utf8'), stored_password)
