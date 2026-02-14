#!/usr/bin/env python3
"""Generate bcrypt password hash"""
import bcrypt

# Owner password
password = "RaisenOmega2026!"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(f"Owner password hash: {hashed.decode()}")

# Test reseller password
password2 = "Test1234!"
hashed2 = bcrypt.hashpw(password2.encode(), bcrypt.gensalt())
print(f"Reseller password hash: {hashed2.decode()}")

# Temp password for new resellers
password3 = "TempAccess2026!"
hashed3 = bcrypt.hashpw(password3.encode(), bcrypt.gensalt())
print(f"Temp password hash: {hashed3.decode()}")
