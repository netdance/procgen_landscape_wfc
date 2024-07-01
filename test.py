import time

# Comparing integers
start_time = time.time()
for i in range(1000000):
    if 1 == 1:
        pass
int_time = time.time() - start_time

# Comparing single-character strings
start_time = time.time()
for i in range(1000000):
    if 'a' == 'a':
        pass
str_time = time.time() - start_time

# Comparing integers
start_time = time.time()
for i in range(1000000):
    if 1 == 1:
        pass
int_time = time.time() - start_time


print(f"Integer comparison time: {int_time}")
print(f"Single-character string comparison time: {str_time}")