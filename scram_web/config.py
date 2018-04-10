import yaml

yaml_data = file('scram_web/config.yaml','r')
raw_data = yaml.load(yaml_data)

server_host = raw_data['server_settings']['server_host']
server_port = raw_data['server_settings']['server_port']
server_debug = raw_data['server_settings']['server_debug']

if server_debug:
    print("Data loaded from config.py: ",server_host,server_port,server_debug)

# TODO: add database connection config here

