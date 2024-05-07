import tkinter as tk
from tkinter import messagebox
import threading
import multiprocessing
import concurrent.futures
import random
import time 


class ProcessoValor(multiprocessing.Process):  
    def __init__(self, num_pontos, pontos_dentro_circulo, fila_resultados):
        super().__init__()
        self.num_pontos = num_pontos
        self.pontos_dentro_circulo = pontos_dentro_circulo  
        self.fila_resultados = fila_resultados  

    # FUNÇÃO EXECUTAR
    def run(self):
        pontos_dentro_circulo = parte_pi_monte_carlo(self.num_pontos, self.pontos_dentro_circulo)
        self.fila_resultados.put(pontos_dentro_circulo)

# FUNÇÃO AUXILIAR PARA CALCULAR PONTOS DENTRO DO CÍRCULO
def parte_wrapper_pi_monte_carlo(num_pontos):
    pontos_dentro = 0
    for _ in range(num_pontos):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        distancia_origem = (x ** 2 + y ** 2) ** 0.5
        if distancia_origem <= 1:
            pontos_dentro += 1
    return pontos_dentro

#FUNÇÃO PARA CALCULAR PONTOS DENTRO DO CÍRCULO
def parte_pi_monte_carlo(num_pontos, pontos_dentro_circulo):
    pontos_dentro = 0
    for _ in range(num_pontos):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        distancia_origem = (x ** 2 + y ** 2) ** 0.5
        if distancia_origem <= 1:
            pontos_dentro += 1
    with pontos_dentro_circulo.get_lock():
        pontos_dentro_circulo.value += pontos_dentro
    return pontos_dentro

# CALCULA O PI USANDO concurrent.futures
def monte_carlo_pi_concurrent(num_pontos, num_trabalhadores):  
    tempo_inicio = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_trabalhadores) as executor:
        total_pontos_dentro_circulo = sum(executor.map(parte_wrapper_pi_monte_carlo, [num_pontos // num_trabalhadores] * num_trabalhadores))

    aproximacao_pi = 4 * total_pontos_dentro_circulo / num_pontos
    tempo_fim = time.time()
    return aproximacao_pi, tempo_fim - tempo_inicio

# CALCULA O PI USANDO THREADS
def monte_carlo_pi_threads(num_pontos, num_threads):  
    tempo_inicio = time.time()
    pontos_dentro_circulo = multiprocessing.Value('i', 0)
    threads = []
    pontos_por_thread = num_pontos // num_threads
    semaforo = threading.Semaphore(num_threads) 
    for _ in range(num_threads):
        thread = threading.Thread(target=parte_pi_monte_carlo_com_semaforo, args=(pontos_por_thread, pontos_dentro_circulo, semaforo))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    total_pontos_dentro_circulo = pontos_dentro_circulo.value
    aproximacao_pi = 4 * total_pontos_dentro_circulo / num_pontos
    tempo_fim = time.time()
    return aproximacao_pi, tempo_fim - tempo_inicio

# FUNÇÃO PARA CALCULAR PONTOS DENTRO DO CÍRCULO COM SEMÁFORO
def parte_pi_monte_carlo_com_semaforo(num_pontos, pontos_dentro_circulo, semaforo):  
    semaforo.acquire()
    try:
        pontos_dentro = 0
        for _ in range(num_pontos):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            distancia_origem = (x ** 2 + y ** 2) ** 0.5
            if distancia_origem <= 1:
                pontos_dentro += 1
        with pontos_dentro_circulo.get_lock():
            pontos_dentro_circulo.value += pontos_dentro
    finally:
        semaforo.release()

#CALCULA PI USANDO multiprocessing
def monte_carlo_pi_multiprocessing(num_pontos, num_processos):
    tempo_inicio = time.time()
    pontos_dentro_circulo = multiprocessing.Value('i', 0)
    processos = []
    pontos_por_processo = num_pontos // num_processos
    for _ in range(num_processos):
        processo = multiprocessing.Process(target=parte_pi_monte_carlo, args=(pontos_por_processo, pontos_dentro_circulo))
        processos.append(processo)
        processo.start()
    for processo in processos:
        processo.join()
    total_pontos_dentro_circulo = pontos_dentro_circulo.value
    aproximacao_pi = 4 * total_pontos_dentro_circulo / num_pontos
    tempo_fim = time.time()
    return aproximacao_pi, tempo_fim - tempo_inicio

# CALCULA PI USANDO THREADS E SEMÁFOROS
def monte_carlo_pi_threads_com_semaforo(num_pontos, num_threads):  
    tempo_inicio = time.time()
    pontos_dentro_circulo = multiprocessing.Value('i', 0)
    threads = []
    pontos_por_thread = num_pontos // num_threads
    semaforo = threading.Semaphore(num_threads)
    for _ in range(num_threads):
        thread = threading.Thread(target=parte_pi_monte_carlo_com_semaforo, args=(pontos_por_thread, pontos_dentro_circulo, semaforo))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    total_pontos_dentro_circulo = pontos_dentro_circulo.value
    aproximacao_pi = 4 * total_pontos_dentro_circulo / num_pontos
    tempo_fim = time.time()
    return aproximacao_pi, tempo_fim - tempo_inicio

# SELECIONA A FUNÇÃO DE CÁLCULO DE PI COM BASE NO MÉTODO ESCOLHIDO
def calcular_pi(metodo, num_pontos, num_trabalhadores):
    if metodo == "Threads":
        return monte_carlo_pi_threads(num_pontos, num_trabalhadores)
    elif metodo == "Multiprocessamento":
        return monte_carlo_pi_multiprocessing(num_pontos, num_trabalhadores)
    elif metodo == "Concurrent.Futures":
        return monte_carlo_pi_concurrent(num_pontos, num_trabalhadores)
    elif metodo == "Threads com Semáforo":
        return monte_carlo_pi_threads_com_semaforo(num_pontos, num_trabalhadores)

# FUNÇÃO CHAMADA QUANDO O BOTÃO É CLICADO
def ao_clicar_botao(metodo, entrada_num_trabalhadores): 
    try:
        num_trabalhadores = int(entrada_num_trabalhadores.get())  
        valor_pi, tempo_processo = calcular_pi(metodo, 1000000, num_trabalhadores)
        messagebox.showinfo("Resultado", f"Valor aproximado de Pi ({metodo}): {valor_pi}\nTempo de processamento: {tempo_processo} segundos")  
    except ValueError:
        messagebox.showerror("Erro", "Insira um número válido de workers.")  
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")  

# CRIA A INTERFACE GRÁFICA
def criar_gui(): 
    raiz = tk.Tk() 
    raiz.title("Cálculo de Pi") 
    raiz.geometry("600x250") 

    # FUNÇÃO CHAMADA QUANDO UM MÉTODO É SELECIONADO
    def ao_selecionar_metodo(metodo):  
        frame_metodo.destroy()
        rotulo_num_trabalhadores = tk.Label(raiz, text=f"Insira o número de {metodo.lower()}:")  
        rotulo_num_trabalhadores.pack()
        entrada_num_trabalhadores = tk.Entry(raiz)
        entrada_num_trabalhadores.pack()

        def ao_confirmar():  
            ao_clicar_botao(metodo, entrada_num_trabalhadores)

        botao_confirmar = tk.Button(raiz, text="Confirmar", command=ao_confirmar)  
        botao_confirmar.pack()

        # Botão para voltar ao menu
        botao_voltar_menu = tk.Button(raiz, text="Voltar ao Menu", command=criar_gui)  
        botao_voltar_menu.pack()

    frame_metodo = tk.Frame(raiz)  
    frame_metodo.pack(pady=20)

    for metodo in ["Threads", "Multiprocessamento", "Concurrent.Futures", "Threads com Semáforo"]:  
        botao_metodo = tk.Button(frame_metodo, text=metodo, command=lambda m=metodo: ao_selecionar_metodo(m))  
        botao_metodo.pack(side=tk.LEFT, padx=10)
    raiz.mainloop()

if __name__ == "__main__":
    criar_gui()
