import os
import re
import time
import requests
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, filedialog, scrolledtext
import csv
from bs4 import BeautifulSoup

"""
Este script foi criado para buscar (via Bing) dados de contato (como emails, telefones e links de redes sociais)
para fins de marketing. Esses dados podem ser vendidos ou usados em estratégias de prospecção.
Use somente conforme a legislação de cada país e respeitando a privacidade.

Suporte no Telegram: @astrahvhdev

Para testar, você pode usar a palavra-chave: "SEO services"
Pois costuma retornar sites com e-mails e telefones reais.
"""

# Instala dependências automaticamente
def install_dependencies():
    required = ["requests", "bs4", "tk"]
    for package in required:
        try:
            __import__(package)
        except ImportError:
            os.system(f"pip install {package}")

install_dependencies()

class WebScraperApp:
    def __init__(self, root):
        # ==============  CONFIGURAÇÕES DA JANELA  ==================
        self.root = root
        self.root.title("Web Scraper (Bing) - Contatos de Marketing")
        self.root.configure(bg="#f7f7f7")  # Cor de fundo suave
        self.root.geometry("800x600")  # Tamanho maior
        self.root.update()

        # Iniciando com alpha 0 para animação de fade-in
        self.root.attributes("-alpha", 0.0)
        self.fade_in_window()

        # Fonte personalizada
        self.title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.normal_font = tkfont.Font(family="Segoe UI", size=10)

        # ==============  MENSAGEM DE TOPO  ==================
        self.top_label = tk.Label(
            self.root,
            text=(
                "Este script busca dados de contato (e-mails, telefones, redes sociais)\n"
                "que podem ser usados em estratégias de marketing ou vendidos.\n"
                "Use apenas com a devida permissão e respeito à privacidade.\n"
                "Suporte no Telegram: @astrahvhdev\n\n"
                "Para testar, você pode usar a palavra-chave: \"SEO services\"\n"
                "Pois costuma retornar sites com e-mails e telefones reais."
            ),
            bg="#f7f7f7",
            fg="#333333",
            font=self.normal_font,
            justify=tk.LEFT
        )
        self.top_label.pack(pady=10)

        # ==============  FRAME PARA ENTRADA DE PALAVRAS-CHAVE  ==================
        self.keyword_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.keyword_frame.pack(pady=5)

        self.keyword_label = tk.Label(
            self.keyword_frame,
            text="Digite palavras-chave (ex.: marketing agency):",
            bg="#f7f7f7",
            fg="#000000",
            font=self.normal_font
        )
        self.keyword_label.pack()

        self.keyword_entry = tk.Entry(
            self.keyword_frame,
            width=50,
            font=self.normal_font
        )
        self.keyword_entry.pack(pady=5)

        # ==============  FRAME PARA OS BOTÕES DE AÇÃO  ==================
        self.buttons_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.buttons_frame.pack(pady=5)

        self.search_button = tk.Button(
            self.buttons_frame,
            text="Iniciar Busca",
            command=self.start_search,
            bg="#4caf50",
            fg="#ffffff",
            font=self.normal_font,
            width=15,
            relief="raised"
        )
        self.search_button.grid(row=0, column=0, padx=5, pady=5)
        self.add_hover_effect(self.search_button, hover_bg="#66bb6a")

        self.stop_button = tk.Button(
            self.buttons_frame,
            text="Parar Busca",
            command=self.stop_search,
            bg="#f44336",
            fg="#ffffff",
            font=self.normal_font,
            width=15,
            relief="raised"
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        self.add_hover_effect(self.stop_button, hover_bg="#e57373")

        self.export_csv_button = tk.Button(
            self.buttons_frame,
            text="Exportar CSV",
            command=self.export_csv,
            bg="#2196f3",
            fg="#ffffff",
            font=self.normal_font,
            width=15,
            relief="raised"
        )
        self.export_csv_button.grid(row=1, column=0, padx=5, pady=5)
        self.add_hover_effect(self.export_csv_button, hover_bg="#42a5f5")

        self.export_txt_button = tk.Button(
            self.buttons_frame,
            text="Exportar TXT",
            command=self.export_txt,
            bg="#ff9800",
            fg="#ffffff",
            font=self.normal_font,
            width=15,
            relief="raised"
        )
        self.export_txt_button.grid(row=1, column=1, padx=5, pady=5)
        self.add_hover_effect(self.export_txt_button, hover_bg="#ffb74d")

        # ==============  FRAME PARA FUNÇÕES DE PALAVRAS-CHAVE  ==================
        self.keywords_utils_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.keywords_utils_frame.pack(pady=5)

        self.show_keywords_button = tk.Button(
            self.keywords_utils_frame,
            text="Melhores palavras-chave",
            command=self.show_best_keywords,
            bg="#9c27b0",
            fg="#ffffff",
            font=self.normal_font,
            width=20,
            relief="raised"
        )
        self.show_keywords_button.grid(row=0, column=0, padx=5, pady=5)
        self.add_hover_effect(self.show_keywords_button, hover_bg="#ab47bc")

        self.copy_keywords_button = tk.Button(
            self.keywords_utils_frame,
            text="Copiar Palavras-Chave",
            command=self.copy_best_keywords,
            bg="#795548",
            fg="#ffffff",
            font=self.normal_font,
            width=20,
            relief="raised"
        )
        self.copy_keywords_button.grid(row=0, column=1, padx=5, pady=5)
        self.add_hover_effect(self.copy_keywords_button, hover_bg="#8d6e63")

        # ==============  LABEL DE STATUS  ==================
        self.status_label = tk.Label(
            self.root,
            text="Status: Aguardando busca",
            fg="#333333",
            bg="#f7f7f7",
            font=self.normal_font
        )
        self.status_label.pack(pady=5)

        # ==============  FRAME PARA O LOG (SCROLLEDTEXT)  ==================
        self.log_frame = tk.Frame(self.root, bg="#f7f7f7")
        self.log_frame.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=15,
            width=90,
            font=("Consolas", 9),
            wrap="word"
        )
        self.log_text.pack()

        # Lista para armazenar os resultados (url, emails, telefones, redes sociais)
        self.results = []
        # Flag para controlar se a busca deve continuar
        self.running = False

    def fade_in_window(self, step=0.05):
        """
        Animação de fade-in para a janela, incrementando alpha gradualmente.
        """
        current_alpha = self.root.attributes("-alpha")
        if current_alpha < 1.0:
            new_alpha = current_alpha + step
            if new_alpha > 1.0:
                new_alpha = 1.0
            self.root.attributes("-alpha", new_alpha)
            self.root.after(30, self.fade_in_window)

    def add_hover_effect(self, widget, hover_bg="#dddddd"):
        """
        Adiciona um efeito de hover ao widget, mudando a cor de fundo ao passar o mouse.
        """
        original_bg = widget["bg"]
        def on_enter(e):
            widget["bg"] = hover_bg
        def on_leave(e):
            widget["bg"] = original_bg
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def log(self, message):
        """Escreve mensagens no log e faz scroll automático."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def show_best_keywords(self):
        """
        Mostra algumas palavras-chave que geralmente retornam resultados
        para marketing e negócios, úteis para testar.
        """
        keywords = (
            "marketing agency\n"
            "digital marketing services\n"
            "agência de marketing digital\n"
            "SEO services\n"
            "email marketing solutions\n"
            "lead generation strategy\n"
            "social media marketing\n"
        )
        messagebox.showinfo("Melhores Palavras-Chave", "Algumas sugestões:\n\n" + keywords)

    def copy_best_keywords(self):
        """Copia as sugestões de palavras-chave para a área de transferência."""
        keywords = (
            "marketing agency\n"
            "digital marketing services\n"
            "agência de marketing digital\n"
            "SEO services\n"
            "email marketing solutions\n"
            "lead generation strategy\n"
            "social media marketing\n"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(keywords)
        messagebox.showinfo("Copiado", "Palavras-chave copiadas para a área de transferência!")

    def bing_search(self, query, offset=0):
        """
        Faz a busca no Bing para 'query', com deslocamento 'offset'.
        Cada página do Bing costuma trazer ~10 resultados.
        offset = 0 (página 1), offset = 10 (página 2), etc.
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://www.bing.com/search?q={query}&first={offset}"
        try:
            resp = requests.get(search_url, headers=headers, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            links = []
            for item in soup.select("li.b_algo h2 a"):
                href = item.get("href")
                if href and href.startswith("http"):
                    links.append(href)

            return links
        except requests.exceptions.RequestException as e:
            self.log(f"Erro na busca Bing: {e}")
            return []

    def extract_marketing_contacts(self, url):
        """
        Acessa o site 'url' e extrai e-mails, telefones e links de redes sociais
        (ex.: Facebook, Instagram, LinkedIn, Twitter) para contato.
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            text = response.text

            # Regex para e-mails
            emails = set(re.findall(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                text
            ))

            # Regex para telefones
            phones = set(re.findall(
                r"\+?\d{1,3}?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}",
                text
            ))

            # Regex para redes sociais
            social_patterns = {
                "Facebook": r"(https?://(www\.)?facebook\.com/[^ '\"<]+)",
                "Instagram": r"(https?://(www\.)?instagram\.com/[^ '\"<]+)",
                "LinkedIn": r"(https?://(www\.)?linkedin\.com/[^ '\"<]+)",
                "Twitter": r"(https?://(www\.)?twitter\.com/[^ '\"<]+)"
            }

            socials_found = set()
            for name, pattern in social_patterns.items():
                found = re.findall(pattern, text)
                for match_tuple in found:
                    socials_found.add(f"{name}: {match_tuple[0]}")

            return emails, phones, socials_found
        except requests.exceptions.RequestException as e:
            self.log(f"Falha ao acessar {url}: {e}")
            return set(), set(), set()

    def search(self):
        """
        Faz buscas indefinidamente no Bing, avançando de página em página,
        até o usuário clicar em 'Parar Busca' ou não encontrar mais resultados.
        Coleta e-mails, telefones e redes sociais.
        """
        self.running = True
        query = self.keyword_entry.get().strip()
        if not query:
            messagebox.showerror("Erro", "Digite palavras-chave!")
            return

        offset = 0  # deslocamento inicial
        while self.running:
            page_number = (offset // 10) + 1
            self.status_label.config(text=f"Buscando... (página {page_number})")
            self.log(f"Buscando por: '{query}' na página {page_number}")

            urls = self.bing_search(query, offset=offset)

            if not urls:
                self.log("Nenhuma URL encontrada nesta página. Pode ser fim de resultados ou bloqueio.")
                self.log("Continuando mesmo assim para a próxima página...")

            for url in urls:
                if not self.running:
                    break
                self.log(f"Verificando: {url}")
                emails, phones, socials = self.extract_marketing_contacts(url)
                if emails or phones or socials:
                    self.log(f"Encontrado -> Emails: {emails}, Telefones: {phones}, Redes Sociais: {socials}")
                    self.results.append({
                        "url": url,
                        "emails": list(emails),
                        "phones": list(phones),
                        "socials": list(socials)
                    })
                else:
                    self.log("Nenhum contato encontrado. Aguardando 3s e pulando para o próximo...")
                    time.sleep(3)

                time.sleep(2)

            offset += 10
            time.sleep(3)

        self.running = False
        self.status_label.config(text="Busca concluída ou interrompida!")
        self.log("Fim da busca.")

    def start_search(self):
        search_thread = threading.Thread(target=self.search, daemon=True)
        search_thread.start()

    def stop_search(self):
        self.running = False
        self.status_label.config(text="Busca interrompida!")

    def export_csv(self):
        if not self.results:
            messagebox.showerror("Erro", "Nenhum dado para exportar!")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if filename:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["URL", "Emails", "Telefones", "Redes Sociais"])
                for data in self.results:
                    writer.writerow([
                        data["url"],
                        ", ".join(data["emails"]),
                        ", ".join(data["phones"]),
                        ", ".join(data["socials"])
                    ])
            messagebox.showinfo("Sucesso", "Dados exportados para CSV!")

    def export_txt(self):
        if not self.results:
            messagebox.showerror("Erro", "Nenhum dado para exportar!")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")]
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as file:
                for data in self.results:
                    file.write(f"URL: {data['url']}\n")
                    file.write(f"Emails: {', '.join(data['emails'])}\n")
                    file.write(f"Telefones: {', '.join(data['phones'])}\n")
                    file.write(f"Redes Sociais: {', '.join(data['socials'])}\n\n")
            messagebox.showinfo("Sucesso", "Dados exportados para TXT!")

# Ponto de entrada do script
if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperApp(root)
    root.mainloop()
