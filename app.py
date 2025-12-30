# -*- coding: utf-8 -*-
"""
Created on Tue Dec 30 14:39:34 2025

@author: r2319
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from pypdf import PdfReader, PdfWriter
import io
from datetime import datetime

class SimplePDFSplitter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Divisor de PDF Simple")
        self.root.geometry("500x750")
        
        # Configurar colores
        self.bg_color = "#f8f9fa"
        self.primary_color = "#007bff"
        self.success_color = "#28a745"
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.input_file = ""
        self.output_dir = ""
        self.max_size_mb = 4.0
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Título
        title_frame = tk.Frame(self.root, bg=self.bg_color, pady=20)
        title_frame.pack(fill=tk.X)
        
        title = tk.Label(title_frame, 
                        text="✂️ Divisor de PDF Simple",
                        font=("Arial", 18, "bold"),
                        bg=self.bg_color,
                        fg=self.primary_color)
        title.pack()
        
        subtitle = tk.Label(title_frame,
                           text="Selecciona un PDF y divídelo en partes de menos de 4MB",
                           font=("Arial", 10),
                           bg=self.bg_color,
                           fg="#6c757d")
        subtitle.pack()
        
        # Línea separadora
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Sección de selección de archivo
        select_frame = tk.Frame(self.root, bg=self.bg_color, pady=20)
        select_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(select_frame,
                text="1. SELECCIONA UN ARCHIVO PDF:",
                font=("Arial", 11, "bold"),
                bg=self.bg_color).pack(anchor=tk.W, pady=(0, 10))
        
        # Botón grande para seleccionar archivo
        self.select_btn = tk.Button(select_frame,
                                   text="📂 Haz clic para seleccionar PDF",
                                   font=("Arial", 12),
                                   bg=self.primary_color,
                                   fg="white",
                                   relief="flat",
                                   padx=30,
                                   pady=15,
                                   cursor="hand2",
                                   command=self.select_file)
        self.select_btn.pack(fill=tk.X)
        
        # Info del archivo
        self.file_label = tk.Label(select_frame,
                                  text="No hay archivo seleccionado",
                                  font=("Arial", 9),
                                  bg=self.bg_color,
                                  fg="#6c757d",
                                  wraplength=400,
                                  justify=tk.LEFT)
        self.file_label.pack(anchor=tk.W, pady=(10, 0))
        
        # Sección de selección de carpeta de destino
        dest_frame = tk.Frame(self.root, bg=self.bg_color, pady=10)
        dest_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(dest_frame,
                text="2. CARPETA DE DESTINO (OPCIONAL):",
                font=("Arial", 11, "bold"),
                bg=self.bg_color).pack(anchor=tk.W, pady=(0, 10))
        
        self.dest_btn = tk.Button(dest_frame,
                                 text="📁 Seleccionar Carpeta de Destino",
                                 font=("Arial", 10),
                                 bg="#6c757d",
                                 fg="white",
                                 relief="flat",
                                 padx=15,
                                 pady=8,
                                 cursor="hand2",
                                 command=self.select_output_dir)
        self.dest_btn.pack(fill=tk.X)
        
        self.dest_label = tk.Label(dest_frame,
                                  text="Se guardará en la misma carpeta que el original",
                                  font=("Arial", 9),
                                  bg=self.bg_color,
                                  fg="#6c757d",
                                  wraplength=400,
                                  justify=tk.LEFT)
        self.dest_label.pack(anchor=tk.W, pady=(5, 0))

        # Línea separadora
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Sección de configuración
        config_frame = tk.Frame(self.root, bg=self.bg_color, pady=10)
        config_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(config_frame,
                text="3. CONFIGURACIÓN:",
                font=("Arial", 11, "bold"),
                bg=self.bg_color).pack(anchor=tk.W, pady=(0, 10))
        
        # Tamaño máximo
        size_frame = tk.Frame(config_frame, bg=self.bg_color)
        size_frame.pack(anchor=tk.W, pady=5)
        
        tk.Label(size_frame,
                text="Tamaño máximo por parte:",
                bg=self.bg_color).pack(side=tk.LEFT)
        
        self.size_var = tk.StringVar(value="4.0")
        size_entry = tk.Entry(size_frame,
                             textvariable=self.size_var,
                             width=8,
                             justify=tk.CENTER)
        size_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(size_frame,
                text="MB",
                bg=self.bg_color).pack(side=tk.LEFT)
        
        # Línea separadora
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        # Botón de acción
        self.split_btn = tk.Button(self.root,
                                  text="🚀 INICIAR DIVISIÓN",
                                  font=("Arial", 14, "bold"),
                                  bg=self.success_color,
                                  fg="white",
                                  relief="flat",
                                  padx=30,
                                  pady=15,
                                  cursor="hand2",
                                  state=tk.DISABLED,
                                  command=self.start_split)
        self.split_btn.pack(pady=20)
        
        # Área de mensajes
        self.message_text = tk.Text(self.root,
                                   height=10,
                                   width=50,
                                   font=("Consolas", 9),
                                   bg="#f5f5f5",
                                   relief="flat")
        self.message_text.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)
        
        # Configurar scroll
        scrollbar = tk.Scrollbar(self.message_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.message_text.yview)
    
    def select_file(self):
        """Abre el explorador para seleccionar archivo"""
        filetypes = [
            ("Archivos PDF", "*.pdf"),
            ("Todos los archivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Selecciona un archivo PDF",
            filetypes=filetypes
        )
        
        if filename:
            self.input_file = filename
            self.update_file_info()
            self.split_btn.config(state=tk.NORMAL, bg=self.success_color)
            self.log(f"✅ Seleccionado: {os.path.basename(filename)}")
    
    def select_output_dir(self):
        """Abre el explorador para seleccionar carpeta de destino"""
        directory = filedialog.askdirectory(
            title="Selecciona la carpeta donde se guardarán los resultados"
        )
        
        if directory:
            self.output_dir = directory
            self.dest_label.config(text=f"📂 Guardar en: {directory}", fg=self.primary_color)
            self.log(f"📂 Carpeta de destino: {directory}")
    
    def update_file_info(self):
        """Actualiza la información del archivo"""
        if not self.input_file:
            return
        
        try:
            # Obtener información básica
            file_size = os.path.getsize(self.input_file) / (1024 * 1024)
            
            # Leer PDF
            reader = PdfReader(self.input_file)
            page_count = len(reader.pages)
            
            # Actualizar label
            info_text = (f"📄 {os.path.basename(self.input_file)}\n"
                        f"📦 Tamaño: {file_size:.2f} MB\n"
                        f"📄 Páginas: {page_count}")
            
            self.file_label.config(text=info_text)
            
            # Color según tamaño
            if file_size <= 4:
                color = "#28a745"  # Verde
            elif file_size <= 10:
                color = "#fd7e14"  # Naranja
            else:
                color = "#dc3545"  # Rojo
            
            self.file_label.config(fg=color)
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
    
    def start_split(self):
        """Inicia el proceso de división"""
        if not self.input_file:
            return
        
        try:
            # Obtener configuración
            self.max_size_mb = float(self.size_var.get())
            
            if self.max_size_mb <= 0:
                messagebox.showerror("Error", "El tamaño debe ser mayor a 0")
                return
            
            # Deshabilitar botones
            self.split_btn.config(state=tk.DISABLED, text="PROCESANDO...")
            self.select_btn.config(state=tk.DISABLED)
            
            # Realizar división
            self.root.after(100, self.perform_split)
            
        except ValueError:
            messagebox.showerror("Error", "Tamaño inválido")
            self.split_btn.config(state=tk.NORMAL, text="🚀 INICIAR DIVISIÓN")
    
    def perform_split(self):
        """Realiza la división del PDF"""
        try:
            self.log("\n" + "="*50)
            self.log("INICIANDO DIVISIÓN")
            self.log("="*50)
            
            # Determinar base de la carpeta destino
            input_dir = self.output_dir if self.output_dir else os.path.dirname(self.input_file)
            base_name = os.path.splitext(os.path.basename(self.input_file))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{base_name}_partes_{timestamp}"
            output_folder = os.path.join(input_dir, folder_name)
            
            if os.path.exists(output_folder):
                import shutil
                shutil.rmtree(output_folder)
            
            os.makedirs(output_folder)
            
            self.log(f"📁 Creando carpeta: {output_folder}")
            
            # Leer PDF
            reader = PdfReader(self.input_file)
            total_pages = len(reader.pages)
            
            # Dividir PDF
            max_size_bytes = self.max_size_mb * 1024 * 1024
            safety_factor = 0.9
            
            parts = []
            current_writer = PdfWriter()
            current_pages = []
            current_size = 0
            part_num = 1
            
            for page_idx in range(total_pages):
                # Calcular tamaño de página
                temp_writer = PdfWriter()
                temp_writer.add_page(reader.pages[page_idx])
                
                buffer = io.BytesIO()
                temp_writer.write(buffer)
                page_size = len(buffer.getvalue())
                
                # Verificar límite
                if (current_size + page_size > max_size_bytes * safety_factor 
                    and current_pages):
                    # Guardar parte
                    self.save_part(current_writer, current_pages, 
                                 output_folder, base_name, part_num)
                    parts.append((current_pages, current_size))
                    
                    # Reiniciar
                    current_writer = PdfWriter()
                    current_pages = []
                    current_size = 0
                    part_num += 1
                
                # Agregar página
                current_writer.add_page(reader.pages[page_idx])
                current_pages.append(page_idx)
                current_size += page_size
                
                # Actualizar log
                progress = (page_idx + 1) / total_pages * 100
                self.log(f"📊 Progreso: {progress:.1f}%", update=True)
            
            # Guardar última parte
            if current_pages:
                self.save_part(current_writer, current_pages, 
                             output_folder, base_name, part_num)
            
            # Mostrar resumen
            self.show_summary(output_folder, part_num)
            
            # Habilitar botones
            self.split_btn.config(state=tk.NORMAL, text="🚀 INICIAR DIVISIÓN")
            self.select_btn.config(state=tk.NORMAL)
            
            # Preguntar si abrir carpeta
            if messagebox.askyesno("Completado", 
                                 f"¡PDF dividido en {part_num} partes!\n\n"
                                 f"¿Deseas abrir la carpeta destino?"):
                self.open_folder(output_folder)
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            self.split_btn.config(state=tk.NORMAL, text="🚀 INICIAR DIVISIÓN")
            self.select_btn.config(state=tk.NORMAL)
    
    def save_part(self, writer, page_indices, output_folder, base_name, part_num):
        """Guarda una parte del PDF"""
        output_file = os.path.join(output_folder, f"{base_name}_parte_{part_num:03d}.pdf")
        
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        self.log(f"✅ Parte {part_num:03d}: "
                f"páginas {page_indices[0]+1}-{page_indices[-1]+1}, "
                f"{size_mb:.2f} MB")
    
    def show_summary(self, output_folder, total_parts):
        """Muestra resumen del proceso"""
        self.log("\n" + "="*50)
        self.log("🎉 PROCESO COMPLETADO")
        self.log("="*50)
        self.log(f"📦 Total partes: {total_parts}")
        self.log(f"📁 Carpeta: {output_folder}")
        self.log("="*50)
    
    def open_folder(self, folder_path):
        """Abre la carpeta en el explorador"""
        try:
            if os.name == 'nt':
                os.startfile(folder_path)
            elif os.name == 'posix':
                import subprocess
                subprocess.run(['open', folder_path] if os.uname().sysname == 'Darwin' 
                             else ['xdg-open', folder_path])
        except:
            pass
    
    def log(self, message, update=False):
        """Agrega un mensaje al log"""
        if update:
            # Reemplazar última línea
            self.message_text.delete("end-2l", "end-1l")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.message_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.message_text.see(tk.END)
        self.root.update()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

# Instalador automático
def check_dependencies():
    """Verifica e instala dependencias necesarias"""
    try:
        from pypdf import PdfReader
        return True
    except ImportError:
        print("🔧 Instalando dependencias necesarias...")
        import subprocess
        import sys
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
            print("✅ Dependencias instaladas correctamente")
            return True
        except:
            print("❌ Error al instalar dependencias")
            print("Por favor instala manualmente: pip install pypdf")
            return False

def main():
    """Función principal"""
    # Verificar dependencias
    if not check_dependencies():
        input("Presiona Enter para salir...")
        return
    
    # Crear y ejecutar aplicación
    app = SimplePDFSplitter()
    app.run()

if __name__ == "__main__":
    main()