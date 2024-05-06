import tkinter as tk
from tkinter import messagebox
import threading
import multiprocessing
import concurrent.futures
import random
import time 

class ValueProcess(multiprocessing.Process):  
    def __init__(self, num_points, points_inside_circle, result_queue):
        super().__init__()
        self.num_points = num_points
        self.points_inside_circle = points_inside_circle  
        self.result_queue = result_queue  

    def run(self):
        points_inside_circle = monte_carlo_pi_part(self.num_points, self.points_inside_circle)
        self.result_queue.put(points_inside_circle)

def monte_carlo_pi_part_wrapper(num_points):
    points_inside = 0
    for _ in range(num_points):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        distance_to_origin = (x ** 2 + y ** 2) ** 0.5
        if distance_to_origin <= 1:
            points_inside += 1
    return points_inside

def monte_carlo_pi_part(num_points, points_inside_circle):
    points_inside = 0
    for _ in range(num_points):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        distance_to_origin = (x ** 2 + y ** 2) ** 0.5
        if distance_to_origin <= 1:
            points_inside += 1
    with points_inside_circle.get_lock():
        points_inside_circle.value += points_inside
    return points_inside

def monte_carlo_pi_concurrent(num_points, num_workers):  
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        total_points_inside_circle = sum(executor.map(monte_carlo_pi_part_wrapper, [num_points // num_workers] * num_workers))

    pi_approximation = 4 * total_points_inside_circle / num_points
    end_time = time.time()
    return pi_approximation, end_time - start_time

def monte_carlo_pi_threads(num_points, num_threads):  
    start_time = time.time()
    points_inside_circle = multiprocessing.Value('i', 0)
    threads = []
    points_per_thread = num_points // num_threads
    semaphore = threading.Semaphore(num_threads) 
    for _ in range(num_threads):
        thread = threading.Thread(target=monte_carlo_pi_part_with_semaphore, args=(points_per_thread, points_inside_circle, semaphore))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    total_points_inside_circle = points_inside_circle.value
    pi_approximation = 4 * total_points_inside_circle / num_points
    end_time = time.time()
    return pi_approximation, end_time - start_time

def monte_carlo_pi_part_with_semaphore(num_points, points_inside_circle, semaphore):  
    semaphore.acquire()
    try:
        points_inside = 0
        for _ in range(num_points):
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            distance_to_origin = (x ** 2 + y ** 2) ** 0.5
            if distance_to_origin <= 1:
                points_inside += 1
        with points_inside_circle.get_lock():
            points_inside_circle.value += points_inside
    finally:
        semaphore.release()

def monte_carlo_pi_multiprocessing(num_points, num_processes):
    start_time = time.time()
    points_inside_circle = multiprocessing.Value('i', 0)
    processes = []
    points_per_process = num_points // num_processes
    for _ in range(num_processes):
        process = multiprocessing.Process(target=monte_carlo_pi_part, args=(points_per_process, points_inside_circle))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
    total_points_inside_circle = points_inside_circle.value
    pi_approximation = 4 * total_points_inside_circle / num_points
    end_time = time.time()
    return pi_approximation, end_time - start_time

def monte_carlo_pi_threads_with_semaphore(num_points, num_threads):  
    start_time = time.time()
    points_inside_circle = multiprocessing.Value('i', 0)
    threads = []
    points_per_thread = num_points // num_threads
    semaphore = threading.Semaphore(num_threads)
    for _ in range(num_threads):
        thread = threading.Thread(target=monte_carlo_pi_part_with_semaphore, args=(points_per_thread, points_inside_circle, semaphore))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    total_points_inside_circle = points_inside_circle.value
    pi_approximation = 4 * total_points_inside_circle / num_points
    end_time = time.time()
    return pi_approximation, end_time - start_time

def calculate_pi(method, num_points, num_workers):
    if method == "Threads":
        return monte_carlo_pi_threads(num_points, num_workers)
    elif method == "Multiprocessamento":
        return monte_carlo_pi_multiprocessing(num_points, num_workers)
    elif method == "Concurrent.Futures":
        return monte_carlo_pi_concurrent(num_points, num_workers)
    elif method == "Threads com Semáforo":
        return monte_carlo_pi_threads_with_semaphore(num_points, num_workers)

def on_button_click(method, num_workers_entry): 
    try:
        num_workers = int(num_workers_entry.get())
        pi_value, process_time = calculate_pi(method, 1000000, num_workers)
        messagebox.showinfo("Resultado", f"Valor aproximado de Pi ({method}): {pi_value}\nTempo de processamento: {process_time} segundos")
    except ValueError:
        messagebox.showerror("Erro", "Insira um número válido de workers.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")


def create_gui(): 
    def back_to_menu():  # Função para voltar ao menu principal
        root.destroy()  # Fecha a janela atual
        create_gui()    # Chama a função create_gui() novamente para voltar ao menu principal

    root = tk.Tk() 
    root.title("Cálculo de Pi") 
    root.geometry("600x250") 

    method_frame = tk.Frame(root)  
    method_frame.pack(pady=20)

    for method in ["Threads", "Multiprocessamento", "Concurrent.Futures", "Threads com Semáforo"]:  
        method_button = tk.Button(method_frame, text=method, command=lambda m=method: on_method_selected(m))  
        method_button.pack(side=tk.LEFT, padx=10)
    
    back_button = tk.Button(root, text="Voltar ao Menu", command=back_to_menu)  # Botão para voltar ao menu
    back_button.pack(side=tk.BOTTOM, pady=10)

    def on_method_selected(method):  
        method_frame.destroy()
        num_workers_label = tk.Label(root, text=f"Insira o número de {method.lower()}:")  
        num_workers_label.pack()
        num_workers_entry = tk.Entry(root)
        num_workers_entry.pack()

        def on_confirm():  
            on_button_click(method, num_workers_entry)

        confirm_button = tk.Button(root, text="Confirmar", command=on_confirm)  
        confirm_button.pack()

    root.mainloop()


if __name__ == "__main__":
    create_gui()
