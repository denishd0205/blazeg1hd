


def Operacao50(demo, amount=2, stop_gain=None, stop_loss=None, martingale=None):
    global count_win, count_loss, current_amount, \
        is_gale, count_martingale
    
    numero_entrada = 0

    is_gale = None
    count_loss = 0
    before_enter = None

    balance = float(get_balance()["balance"]) if not demo else float(10000)
    current_balance, first_balance = (float(balance), float(balance))
    current_amount, first_amount = (float(amount), float(amount))

    report_data = []
    init_bets = real_bets
    last_doubles = ba.get_last_doubles()
    if demo:
        print("AMBIENTE DE TESTES")
        init_bets = fake_bets
    if config_user["status"] == "disable":
        print("ESTRATÉGIAS DO SISTEMA | ANALISANDO ENTRADA...\r")
    while True: #numero_entrada <= total_entradas #count_martingale <= martingale:
        status = ba.get_status() == "waiting"
        
        #A favor da tendencia (nao ir contra tendencia)
        if last_doubles:
            double = [[item["color"], item["value"]] for item in last_doubles["items"]]
            colored_string = ', '.join([
                f"\033[10;40m {item[1]} \033[m" if item[0] == "preto"
                else f"\033[10;41m {item[1]} \033[m" if item[0] == "vermelho"
                else f"\033[10;47m {item[1]} \033[m" for item in double[:5]])

            vermelho_tendencia = [color[0] for color in double[:5]].count("vermelho")
            preto_tendencia = [color[0] for color in double[:5]].count("vermelho")
            if vermelho_tendencia >= 5 or preto_tendencia >= 5:
                print(f'Tendência de {vermelho_tendencia} velas da mesma cor, identificada.')
                print(f"\r{colored_string}\n")
                print('Esperando passar tentência')
                color_enter = None
            else:
                if not is_gale:
                    color_enter = get_colors_by_doubles() if not config_user["status"] == "enable" else get_user_analises()
                    before_enter = color_enter
                else:
                    color_enter = before_enter
                    print(f'PRÓXIMA ENTRADA SERÁ DE: {current_amount}\r')

        # A favor da tendencia inverter cor entrada
        if against_trend == 1:
            color_enter = "preto" if before_enter == "vermelho" else "vermelho"
        if status and color_enter:
            gnm.todas_entradas+=1
            #if numero_entrada <= total_entradas: #count_martingale <= martingale:
            single_bet = init_bets(color_enter, amount=current_amount, balance=current_balance)
            report_data.append(single_bet)
            if not single_bet["object"]["win"]:

                # Não permite valor menor que o valor inicial
                if current_amount < first_amount:
                    current_amount = first_amount

                current_amount = current_amount * 1.475
                
                gnm.contador_loss += 1
                gnm.quantidade_loss_geral+=1
                numero_entrada+=1

                # Calcular martingale
                #current_amount = calculate_martingale(current_amount)

                print('gnm.contador_win', gnm.contador_win)
                print('gnm.contador_loss', gnm.contador_loss)

            else:
                # Não permite valor menor que o valor inicial
                if current_amount < first_amount:
                    current_amount = first_amount
                gnm.contador_win += 1
                gnm.quantidade_win_geral+=1
                count_win += 1
                is_gale = False
                count_martingale = 0
                current_amount = current_amount * 0.8
                #current_amount = first_amount
            
            if total_win_permitido > 0 and (gnm.contador_win >= total_win_permitido):
                current_amount = amount
                print(f'Reiniciando Ciclo após {gnm.contador_win} win')
                gnm.contador_win = 0
                gnm.contador_loss = 0
                numero_entrada = 10000
            
            if total_loss_permitido > 0 and (gnm.contador_loss >= total_loss_permitido):
                current_amount = amount
                print(f'Reiniciando Ciclo após {gnm.contador_loss} loss')
                gnm.contador_win = 0
                gnm.contador_loss = 0
                numero_entrada = 10000

            current_balance = single_bet.get("object")["balance"]
            profit = round(current_balance - first_balance, 2)
            if profit < 0:
                print(f"⛔️ ESTAMOS NEGATIVO: {profit}\r")
            elif profit == 0:
                print(f"🟫 ESTAMOS NO 0 X 0 : {profit}\r")
            elif profit > 0:
                print(f"✅ ESTAMOS GANHANDO: {profit}\r")
            
            if gnm.todas_entradas % 6 == 0:
                print(f"\n📣 Total Win: {gnm.quantidade_win_geral} ✅")
                print(f"📣 Total Loss: {gnm.quantidade_loss_geral} ❌\n")

            if stop_gain and profit >= abs(stop_gain):
                print("LIMITE DE GANHOS BATIDO, AGUARDANDO...")
                report_save(report_type, report_data, "stop_gain")
                first_balance = current_balance
                is_gale = False
                count_loss = 0
                if sleep_bot > 0:
                    time.sleep(sleep_bot)
                else:
                    break
            elif count_loss >= stop_loss:
                print("LIMITE DE PERDAS BATIDO, AGUARDANDO...")
                report_save(report_type, report_data, "stop_loss")
                first_balance = current_balance
                if sleep_bot > 0:
                    time.sleep(sleep_bot)
                    is_gale = False
                    count_loss = 0
                else:
                    break
            # print(json.dumps(single_bet, indent=4))
        numero_entrada +=1
        time.sleep(6)