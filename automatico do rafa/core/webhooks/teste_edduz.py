import requests

class Eduzz:
    def __init__(self, email, public_key='14451229', api_key='3126281419'):
        self.email = email
        self.public_key = public_key
        self.api_key = api_key

        self.headers = {'token': self.get_token()}
        

    def get_token(self):
        method_url = 'https://api2.eduzz.com/credential/generate_token'
        payload = {'email': self.email, 'publickey': self.public_key, 'apikey' : self.api_key}

        try:
            r = requests.post(url = method_url, params = payload)
            data = r.json()
            return data.get('data', None).get('token', None)
        except:
            return None
        
    def get_sale_list(self, start_date, end_date, page = None, contract_id=None, affiliate_id=None,
                    content_id=None, invoice_status=None, client_email=None,
                    client_document=None, date_type=None):

        method_url = 'https://api2.eduzz.com/sale/get_sale_list'
        headers = {'token': self.get_token()}
        payload = {'start_date': start_date, 'end_date': end_date}
        
        if page:
            payload['page'] = page
        if contract_id:
            payload['contract_id'] = contract_id
        if affiliate_id:
            payload['affiliate_id'] = affiliate_id
        if content_id:
            payload['content_id'] = content_id
        if invoice_status:
            payload['invoice_status'] = invoice_status
        if client_email:
            payload['client_email'] = client_email
        if client_document:
            payload['client_document'] = client_document
        if date_type:
            payload['date_type'] = date_type
            
        
        try:
            r = requests.get(url = method_url, headers = self.headers, params = payload)
            data = r.json()
            return data
        except: 
            return None


    def user_admin(self):
        method_url = 'https://api2.eduzz.com/user/get_me'
        try:
            r = requests.get(url = method_url, headers=self.headers)
            data = r.json()
            return data
        except:
            return None
    

    def balance(self):
        method_url = 'https://api2.eduzz.com/financial/balance'
        try:
            r = requests.get(url = method_url, headers=self.headers)
            data = r.json()
            return data
        except:
            return None
        

    def get_status(self):
        method_url = 'https://api2.eduzz.com/subscription/status_list/'
        headers = {'token': self.get_token()}
        try:
            r = requests.get(url = method_url, headers = headers)
            data = r.json()
            print(data)
            return data
        except: 
            return None


    def get_contract_id(self, id):
        method_url = f'https://api2.eduzz.com/subscription/get_contract/{id}'
        headers = {'token': self.get_token()}
        params = {'id': id}
        #payment_repeat_type = M(mensal)
        try:
            r = requests.get(url = method_url, headers = headers)
            data = r.json()
            return data
        except: 
            return None
        
    def get_client_id(self, id):
        method_url = f'https://api2.eduzz.com/subscription/{id}/client'
        headers = {'token': self.get_token()}
        params = {'id': id}
        #payment_repeat_type = M(mensal)
        try:
            r = requests.get(url = method_url, headers = headers)
            data = r.json()
            return data
        except: 
            return None


    def get_contract_list(self, start_date, end_date, page = None, client_name=None, contract_status=None,
                    product_id=None, invoice_status=None, client_email=None,
                    product_name=None):

        method_url = 'https://api2.eduzz.com/subscription/get_contract_list'
        headers = {'token': self.get_token()}
        payload = {'start_date': start_date, 'end_date': end_date}
        
        if page:
            payload['page'] = page
        if client_name:
            payload['client_name'] = client_name
        if contract_status:
            payload['contract_status'] = contract_status
        if product_id:
            payload['product_id'] = product_id
        if invoice_status:
            payload['invoice_status'] = invoice_status
        if client_email:
            payload['client_email'] = client_email
        if product_name:
            payload['product_name'] = product_name

        
        try:
            r = requests.get(url = method_url, headers = headers, params = payload)
            data = r.json()
            return data
        except: 
            return None
        
#41733470
    
if __name__ == '__main__':

    eduzz = Eduzz(
	email='lukasmulekezika2@gmail.com',
	public_key='14451229',
	api_key='3126281419'
    )

    # response = eduzz.get_sale_list(start_date='2021-05-03', end_date='2022-09-17')
    # n=0
    # for x in response['data']:
    #     n+=1
    #     print('Cliente: ', x['client_id'])
    #     print('Cliente: ', x['client_name'])
    #     print('Email: ', x['client_email'])
    #     print('Status nome: ', x['sale_status_name'])
    #     print('N° status: ', x['sale_status'])
    #     print('Contrato ID: ', x['contract_id'])
    #     print('Data criada: ', x['date_create'])
    #     print('Data pagamento: ', x['date_payment'])
    #     print('Produto ID: ', x['content_id'])
    #     print('Produto: ', x['content_title'])
        
    #     print('N°', n)
    #     print('-'*40)


    # status_user = eduzz.get_contract_list(start_date='2021-06-03', end_date='2022-05-30')
    # n=0
    # for x in status_user['data']:
    #     n+=1
    #     print(x['client_name'])
    #     print(x['client_email'])
    #     print(x['contract_status'])
    #     print(x['product_id'])
    #     print(x['product_name'])
    #     print('N°', n)
    #     print('-'*30)


    # status = eduzz.get_contract_id(id=767140)
    # lista = []
    # for x in status['data']:
    #     print(x)
    #     n=0
    #     for invoices in x['invoices']:
    #         n+=1
    #         lista.append([f"{invoices['creation_date']} á {invoices['due_date']}", invoices['status_name'], invoices['status']])
    #         print('N°', n)
    # print(lista[-1])

    cliente = eduzz.get_client_id(id=767140)
    print(cliente)