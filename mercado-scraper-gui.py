import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
import threading

def executar_busca():
    termo = entry.get().strip()
    if not termo:
        messagebox.showwarning("Aviso", "Digite um termo de busca.")
        btn_buscar.config(state="normal")
        return

    status_label.config(text="Buscando até 5 produtos...")

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

    driver = webdriver.Chrome(options=options)

    produtos = []
    try:
        url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
        driver.get(url)
        time.sleep(random.uniform(4, 6))

        if "captcha" in driver.page_source.lower():
            messagebox.showerror("Erro", "CAPTCHA detectado. Tente novamente mais tarde.")
            return

        items = driver.find_elements(By.CSS_SELECTOR, "a.poly-component__title")
        links = [item.get_attribute("href") for item in items if item.get_attribute("href")][:5]

        for link in links:
            try:
                driver.get(link)
                time.sleep(random.uniform(4, 7))

                try:
                    nome = driver.find_element(By.CSS_SELECTOR, "h1.ui-pdp-title").text
                except:
                    nome = "Desconhecido"

                try:
                    preco = driver.find_element(By.CSS_SELECTOR, "span.andes-money-amount__fraction").text
                    preco = preco.replace(".", "").replace(",", ".")
                    preco = float(preco)
                except:
                    preco = 0.0

                try:
                    marca = "Desconhecida"
                    specs = driver.find_elements(By.CSS_SELECTOR, "p.ui-vpp-highlighted-specs__key-value__labels__key-value")
                    for spec in specs:
                        spans = spec.find_elements(By.TAG_NAME, "span")
                        if spans and "Marca" in spans[0].text:
                            marca = spans[1].text.strip()
                            break
                except:
                    marca = "Desconhecida"

                produtos.append({
                    "nome": nome,
                    "marca": marca,
                    "preco": preco,
                    "link": link
                })

            except Exception as e:
                print(f"Erro: {str(e)}")
                continue

        html = f"""
        <!DOCTYPE html>
        <html lang='pt-br'>
        <head>
            <meta charset='UTF-8'>
            <title>Relatório de Produtos</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ccc; padding: 10px; text-align: left; }}
                th {{ background: #007bff; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                a {{ color: #007bff; text-decoration: none; }}
            </style>
        </head>
        <body>
            <h1>Resultado da busca: {termo}</h1>
            <table>
                <thead>
                    <tr>
                        <th>Produto</th>
                        <th>Marca</th>
                        <th>Preço</th>
                        <th>Link</th>
                    </tr>
                </thead>
                <tbody>
        """
        for p in produtos:
            html += f"""
                <tr>
                    <td>{p['nome']}</td>
                    <td>{p['marca']}</td>
                    <td>R$ {p['preco']:.2f}</td>
                    <td><a href='{p['link']}' target='_blank'>Ver produto</a></td>
                </tr>
            """
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        with open("relatorio.html", "w", encoding="utf-8") as f:
            f.write(html)

        status_label.config(text="Busca finalizada. Relatório gerado.")
        messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    finally:
        driver.quit()
        btn_buscar.config(state="normal")

def buscar_thread():
    btn_buscar.config(state="disabled")
    thread = threading.Thread(target=executar_busca)
    thread.start()


root = tk.Tk()
root.title("Consulta Mercado Livre")
root.geometry("400x200")
root.resizable(False, False)


fonte_titulo = ("Arial", 12)
fonte_normal = ("Arial", 10)

tk.Label(root, 
        text="Digite o que deseja buscar:", 
        font=fonte_titulo).pack(pady=10)

entry = tk.Entry(root, 
                font=fonte_titulo, 
                width=30)
entry.pack()

btn_buscar = tk.Button(root, 
                      text="Buscar", 
                      font=fonte_titulo,
                      command=buscar_thread)
btn_buscar.pack(pady=10)

status_label = tk.Label(root, 
                       text="", 
                       font=fonte_normal)
status_label.pack()

root.mainloop()