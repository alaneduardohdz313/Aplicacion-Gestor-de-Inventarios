import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Inventarios")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")
        
        self.inventory = {}
        self.load_inventory()
        
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        # Título
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="📦 Sistema de Inventarios", 
                              font=("Arial", 20, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=15)
        
        # Frame de entrada de datos
        input_frame = tk.LabelFrame(self.root, text="Agregar/Editar Producto", 
                                   font=("Arial", 12, "bold"), bg="#ecf0f1", padx=20, pady=15)
        input_frame.pack(padx=20, pady=20, fill=tk.X)
        
        # Campos de entrada
        fields_frame = tk.Frame(input_frame, bg="#ecf0f1")
        fields_frame.pack()
        
        tk.Label(fields_frame, text="Código:", font=("Arial", 10), bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.code_entry = tk.Entry(fields_frame, font=("Arial", 10), width=15)
        self.code_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Nombre:", font=("Arial", 10), bg="#ecf0f1").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.name_entry = tk.Entry(fields_frame, font=("Arial", 10), width=20)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Cantidad:", font=("Arial", 10), bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.quantity_entry = tk.Entry(fields_frame, font=("Arial", 10), width=15)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Precio:", font=("Arial", 10), bg="#ecf0f1").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.price_entry = tk.Entry(fields_frame, font=("Arial", 10), width=20)
        self.price_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Botones de acción
        buttons_frame = tk.Frame(input_frame, bg="#ecf0f1")
        buttons_frame.pack(pady=10)
        
        tk.Button(buttons_frame, text="➕ Agregar", command=self.add_product, 
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"), 
                 width=12, cursor="hand2").grid(row=0, column=0, padx=5)
        
        tk.Button(buttons_frame, text="🔄 Actualizar", command=self.update_product, 
                 bg="#3498db", fg="white", font=("Arial", 10, "bold"), 
                 width=12, cursor="hand2").grid(row=0, column=1, padx=5)
        
        tk.Button(buttons_frame, text="🗑️ Eliminar", command=self.delete_product, 
                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), 
                 width=12, cursor="hand2").grid(row=0, column=2, padx=5)
        
        tk.Button(buttons_frame, text="🧹 Limpiar", command=self.clear_fields, 
                 bg="#95a5a6", fg="white", font=("Arial", 10, "bold"), 
                 width=12, cursor="hand2").grid(row=0, column=3, padx=5)
        
        # Frame de búsqueda
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(padx=20, pady=(0, 10))
        
        tk.Label(search_frame, text="🔍 Buscar:", font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())
        
        # Tabla de productos
        table_frame = tk.Frame(self.root, bg="#f0f0f0")
        table_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Crear tabla
        self.tree = ttk.Treeview(table_frame, columns=("Código", "Nombre", "Cantidad", "Precio", "Total"), 
                                show="headings", yscrollcommand=scrollbar.set, height=12)
        
        scrollbar.config(command=self.tree.yview)
        
        # Configurar columnas
        self.tree.heading("Código", text="Código")
        self.tree.heading("Nombre", text="Nombre del Producto")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Precio", text="Precio Unitario")
        self.tree.heading("Total", text="Valor Total")
        
        self.tree.column("Código", width=100, anchor=tk.CENTER)
        self.tree.column("Nombre", width=250, anchor=tk.W)
        self.tree.column("Cantidad", width=100, anchor=tk.CENTER)
        self.tree.column("Precio", width=120, anchor=tk.E)
        self.tree.column("Total", width=120, anchor=tk.E)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Evento de selección
        self.tree.bind("<ButtonRelease-1>", self.on_select)
        
        # Estilo de la tabla
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 9), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        # Frame de resumen
        summary_frame = tk.Frame(self.root, bg="#34495e", height=50)
        summary_frame.pack(fill=tk.X, side=tk.BOTTOM)
        summary_frame.pack_propagate(False)
        
        self.summary_label = tk.Label(summary_frame, text="", font=("Arial", 11, "bold"), 
                                     bg="#34495e", fg="white")
        self.summary_label.pack(pady=12)
    
    def add_product(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        
        try:
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")
            return
        
        if not code or not name:
            messagebox.showerror("Error", "Código y nombre son obligatorios")
            return
        
        if code in self.inventory:
            messagebox.showerror("Error", f"El código {code} ya existe")
            return
        
        self.inventory[code] = {
            "nombre": name,
            "cantidad": quantity,
            "precio": price
        }
        
        self.save_inventory()
        self.refresh_table()
        self.clear_fields()
        messagebox.showinfo("Éxito", "Producto agregado correctamente")
    
    def update_product(self):
        code = self.code_entry.get().strip()
        
        if not code or code not in self.inventory:
            messagebox.showerror("Error", "Seleccione un producto para actualizar")
            return
        
        name = self.name_entry.get().strip()
        
        try:
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad y precio deben ser números válidos")
            return
        
        self.inventory[code] = {
            "nombre": name,
            "cantidad": quantity,
            "precio": price
        }
        
        self.save_inventory()
        self.refresh_table()
        self.clear_fields()
        messagebox.showinfo("Éxito", "Producto actualizado correctamente")
    
    def delete_product(self):
        code = self.code_entry.get().strip()
        
        if not code or code not in self.inventory:
            messagebox.showerror("Error", "Seleccione un producto para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto {code}?"):
            del self.inventory[code]
            self.save_inventory()
            self.refresh_table()
            self.clear_fields()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
    
    def clear_fields(self):
        self.code_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.code_entry.focus()
    
    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item["values"]
            
            self.clear_fields()
            self.code_entry.insert(0, values[0])
            self.name_entry.insert(0, values[1])
            self.quantity_entry.insert(0, values[2])
            self.price_entry.insert(0, values[3].replace("$", "").replace(",", ""))
    
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get().lower()
        total_products = 0
        total_value = 0
        
        for code, data in self.inventory.items():
            if search_term in code.lower() or search_term in data["nombre"].lower():
                total = data["cantidad"] * data["precio"]
                self.tree.insert("", tk.END, values=(
                    code,
                    data["nombre"],
                    data["cantidad"],
                    f"${data['precio']:,.2f}",
                    f"${total:,.2f}"
                ))
                total_products += data["cantidad"]
                total_value += total
        
        self.summary_label.config(
            text=f"Total de productos: {len(self.inventory)} | Unidades en stock: {total_products} | Valor total del inventario: ${total_value:,.2f}"
        )
    
    def save_inventory(self):
        with open("inventory.json", "w", encoding="utf-8") as f:
            json.dump(self.inventory, f, indent=4, ensure_ascii=False)
    
    def load_inventory(self):
        if os.path.exists("inventory.json"):
            try:
                with open("inventory.json", "r", encoding="utf-8") as f:
                    self.inventory = json.load(f)
            except:
                self.inventory = {}

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManager(root)
    root.mainloop()