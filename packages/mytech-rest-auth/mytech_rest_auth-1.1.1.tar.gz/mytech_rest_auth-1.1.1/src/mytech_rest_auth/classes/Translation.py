class Translation:
    @staticmethod
    def encrypt(message, key):
        encrypted = ""
        for char in message:
            if char.isalpha():
                shifted = ord(char) + key
                if char.isupper():
                    if shifted > ord('Z'):
                        shifted -= 26
                    elif shifted < ord('A'):
                        shifted += 26
                else:
                    if shifted > ord('z'):
                        shifted -= 26
                    elif shifted < ord('a'):
                        shifted += 26
                encrypted += chr(shifted)
            else:
                encrypted += char
        return encrypted

    @staticmethod
    def decrypt( message, key):
        return Translation.encrypt(message, -key)


