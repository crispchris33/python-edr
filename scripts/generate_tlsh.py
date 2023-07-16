import sys
import tlsh

def generate_tlsh(filename):
    with open(filename, 'rb') as f:
        data = f.read()
        return tlsh.hash(data)

print(generate_tlsh(sys.argv[1]))