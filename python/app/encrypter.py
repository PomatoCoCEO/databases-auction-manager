import random
def enc(string):
    aid = bytearray(); enc = bytearray()
    for i in range(len(string)):
        d = random.randint(0, 255)
        aid.append(d)
        s = string[i]
        enc.append(d ^ s)
    return aid, enc

def dec(key, enc):
    ans = ""
    for i in range(len(enc)):
        ans+=(chr(key[i] ^ enc[i]))
    return ans

def dec_file(nameFile):
    with open(nameFile, 'rb') as file:
        tot = file.read()
        l = len(tot)
        key = tot[:l//2]
        enc_info = tot[l//2:]
        return dec(key, enc_info)

def enc_file(srcFile, destFile):
    tot=""
    with open(srcFile, 'rb') as file:
        tot = file.read()
    a = enc(tot)
    s = bytearray(a[0]+a[1])
    with open(destFile,'wb') as file:
        file.write(s)


if __name__=="__main__":
    '''
    a = enc('banana')
    with open('enc.crypto', 'wb') as enc_file:
        s=bytearray(a[0]+a[1])
        enc_file.write(s)
    
    with open('enc.crypto', 'rb') as enc_file:
        tot=enc_file.read()
        l = len(tot)
        key = tot[:l/2]
        enc_info = tot[l/2:]
        print(dec(key, enc_info))
        '''
    
    # enc_file('.creds', '.creds_crypto')
    ret = dec_file('.creds_crypto')
    ar = ret.split(',')
    print('User: %s' % ar[0])
    print('Password: %s' % ar[1])
    print('Host: %s' % ar[2])
    print('Database: %s' % ar[3])