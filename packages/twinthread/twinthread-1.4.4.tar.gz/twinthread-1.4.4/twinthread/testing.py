from twinthread import TwinThreadClient

username = 'brad.johnson@twinthread.com'
base_url = "https://app.twinthread.com"

client = TwinThreadClient(base_url=base_url)
client.login(username)
client.set_context({"taskId": 5039, "assetModelId": 122})

data = client.get_input_data()
client.save_table(data, 'dataset')



