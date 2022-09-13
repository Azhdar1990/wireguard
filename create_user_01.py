# This script create user in wierguard.
# You need install apt install wireguard-tools -y and apt install qrencode on your host to cenerate keys and qr code.
import os

# Variables
parent_dir = "./config" # wireguard configuration dirrectory
wireguard_subnet = "10.13.14" # type here wireguard subnet for clients. Only first 3 octet.
wireguard_dns = "10.13.14.1" # type here wireguard local ip address. It also use for dns because wierguard use coredns.
new_number = "0" # this is a number for last octet for client ip address. it will change each time when adding client.
lister_port = "51820" 
endpoint = "1.1.1.1" # host public ip.
allowedips = "0.0.0.0/0" 
wireguard_container_name = "wireguard-01"
#####################################################
def wg_genkey(new_folder,user_name,genkey_command): # user crypto key generation.
    os.system(genkey_command)
    # print(f'Privatekey and publickey for {user_name} are created.') # user crypto key generation.

def wgconf(new_folder,user_name): # adding user informaton to config file.
    global new_number
    try:
        with open(f'{parent_dir}/wg0.conf', encoding='utf-8-sig') as file: # 
            wg0conf = file.read()
            peer = wg0conf.split('[Peer]') 
            last_peer = peer[-1].replace('\n','').split('.') # Getting last Peer information.
            last_number = int(last_peer[-1].split('/')[0]) # Getting last digit of ip address.
            new_number = str(last_number + 1) # Adding + 1 to this number.
        #####################################################################################
        with open(f'{new_folder}/publickey_{user_name}', encoding='utf-8-sig') as file: # 
            publickey = file.read().replace('\n','') # Getting user public key.
        #####################################################################################
        with open(f'{parent_dir}/wg0.conf', "a+") as file: # adding information to config file. 
            wg0conf = file.seek(0) 
            data = file.read(100)
            if len(data) > 0:
                file.write("\n")
            file.write("\n")
            file.write("[Peer]\n")
            file.write(f"# {user_name}\n")
            file.write(f"PublicKey = {publickey}\n")
            file.write(f"AllowedIPs = {wireguard_subnet}.{new_number}/32\n")
    except: # If you creating the first user in fresh deployed wireguard, there can be no [Peer] in config file.
            # There fore:
        with open(f'{parent_dir}/wg0.conf', encoding='utf-8-sig') as file: # 
            wg0conf = file.read()
            peer = wg0conf.split('\n')
            last_peer = peer[1].split('.') # Split ip address.
            last_number = int(last_peer[-1])
            new_number = str(last_number + 1) # Adding + 1 to this number.
        with open(f'{new_folder}/publickey_{user_name}', encoding='utf-8-sig') as file: # 
            publickey = file.read().replace('\n','') # Getting user public key.
        #####################################################################################
        with open(f'{parent_dir}/wg0.conf', "a+") as file: # # adding information to config file. 
            wg0conf = file.seek(0)  
            data = file.read(100)
            if len(data) > 0:
                file.write("\n")
            file.write("\n")
            file.write("[Peer]\n")
            file.write(f"# {user_name}\n")
            file.write(f"PublicKey = {publickey}\n")
            file.write(f"AllowedIPs = {wireguard_subnet}.{new_number}/32\n")

def peer_conf_file(user_name,new_folder): # creating user configuration file in his folder.
    global new_number
    with open(f'{new_folder}/privatekey_{user_name}', encoding='utf-8-sig') as file: # 
        privatekey = file.read().replace('\n','') # Getting user private key.
    with open(f'{parent_dir}/server/publickey-server', encoding='utf-8-sig') as file: # 
        srvpubkey= file.read().replace('\n','') # Getting server public key.
    #####################################################################################
    with open(f'{new_folder}/{user_name}.conf', "a+") as file: # dding information to config file.
        wg0conf = file.seek(0)
        data = file.read(100)
        if len(data) > 0:
            file.write("\n")
        file.write("[Interface]\n")
        file.write(f"Address = {wireguard_subnet}.{new_number}\n")
        file.write(f"PrivateKey = {privatekey}\n")
        file.write(f"ListenPort = {lister_port}\n")
        file.write(f"DNS = {wireguard_dns}\n")
        file.write("\n")
        file.write(f"[Peer]\n")
        file.write(f"PublicKey = {srvpubkey}\n")
        file.write(f"Endpoint = {endpoint}:{lister_port}\n")
        file.write(f"AllowedIPs = {allowedips}")

def qrcode(new_folder,user_name): # user QR Code creation.
    os.system(f'/usr/bin/qrencode -t png < {new_folder}/{user_name}.conf -o {new_folder}/{user_name}.png')

def restart_container():
    os.system(f'/usr/bin/docker restart {wireguard_container_name}')

def main():

    while True:
        global new_number
        user_name = input('Type new user: \nExample:\nFirstname_Lastname \nType q to exit \n: ')
        new_folder = os.path.join(parent_dir, user_name) 
        genkey_command = f'/usr/bin/wg genkey | tee {new_folder}/privatekey_{user_name} | /usr/bin/wg pubkey | tee {new_folder}/publickey_{user_name}'
  
        if user_name =='q':
            break
        else:
            if os.path.exists(new_folder):
                print("Sorry that user allready exists.")
                continue
            else:
                os.mkdir(new_folder)
                print(f"Creating new dirrectory for {user_name}")
                wg_genkey(new_folder,user_name,genkey_command)
                wgconf(new_folder,user_name)
                peer_conf_file(user_name,new_folder)
                qrcode(new_folder,user_name)
                restart_container()
                break

if __name__ == "__main__":
    main()
