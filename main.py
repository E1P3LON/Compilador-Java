import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

from lexico import AnalizadorLexico
from sintactico import AnalizadorSintactico
from semantico import AnalizadorSemantico

class CompiladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Compilador Java - Analizador')
        self.root.geometry('1080x820')
        self.root.configure(bg='#1e1e1e')
        self.archivo_actual = None  # ruta del archivo abierto/guardado
        self.configurar_estilo()
        self.crear_widgets()

    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TLabel', background='#1e1e1e', foreground='#d4d4d4', font=('Consolas', 11))
        style.configure('TButton', background='#0e639c', foreground='white', padding=6, font=('Segoe UI', 10, 'bold'))
        style.map('TButton', background=[('active', '#1177bb')])
        
        # Estilos para botones de ejemplos
        style.configure('Correcto.TButton', background='#2e7d32', foreground='white', padding=6, font=('Segoe UI', 9, 'bold'))
        style.map('Correcto.TButton', background=[('active', '#4caf50')])
        
        style.configure('Incorrecto.TButton', background='#c62828', foreground='white', padding=6, font=('Segoe UI', 9, 'bold'))
        style.map('Incorrecto.TButton', background=[('active', '#ef5350')])

    def crear_widgets(self):
        frm = ttk.Frame(self.root)
        frm.pack(fill='both', expand=True, padx=10, pady=10)

        # ----- Barra de menú básica -----
        menubar = tk.Menu(self.root, bg='#2d2d2d', fg='white', tearoff=False)
        menu_archivo = tk.Menu(menubar, tearoff=False, bg='#252526', fg='white')
        menu_archivo.add_command(label='Abrir...', command=self.abrir_archivo)
        menu_archivo.add_command(label='Guardar', command=self.guardar_archivo)
        menu_archivo.add_command(label='Guardar como...', command=self.guardar_como)
        menu_archivo.add_separator()
        menu_archivo.add_command(label='Salir', command=self.root.quit)
        menubar.add_cascade(label='Archivo', menu=menu_archivo)
        self.root.config(menu=menubar)

        ttk.Label(frm, text='Código a analizar:').pack(anchor='w', pady=(0, 6))

        # ----- Contenedor código + números de línea -----
        editor_frame = ttk.Frame(frm)
        editor_frame.pack(fill='both', expand=False)

        # Lienzo para números de línea
        self.line_numbers = tk.Canvas(editor_frame, width=45, bg='#252526', highlightthickness=0)
        self.line_numbers.pack(side='left', fill='y')

        # Text del código
        self.txt_codigo = tk.Text(
            editor_frame,
            wrap='none',
            height=18,
            font=('Consolas', 12),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#d4d4d4',
            undo=True
        )
        self.txt_codigo.pack(side='left', fill='both', expand=True)

        # Scrollbars compartidos
        y_scroll = ttk.Scrollbar(editor_frame, orient='vertical', command=self._on_vertical_scroll)
        y_scroll.pack(side='right', fill='y')
        x_scroll = ttk.Scrollbar(frm, orient='horizontal', command=self.txt_codigo.xview)
        x_scroll.pack(fill='x')

        self.txt_codigo.config(yscrollcommand=lambda *args: self._on_textscroll(*args, y_scroll),
                               xscrollcommand=x_scroll.set)

        # Eventos para actualizar números de línea
        self.txt_codigo.bind('<KeyRelease>', self._actualizar_numeros_linea)
        self.txt_codigo.bind('<MouseWheel>', self._actualizar_numeros_linea)
        self.txt_codigo.bind('<Button-1>', self._actualizar_numeros_linea)
        self.txt_codigo.bind('<Configure>', self._actualizar_numeros_linea)

        btns = ttk.Frame(frm)
        btns.pack(fill='x', pady=8)
        ttk.Button(btns, text='📂 Abrir', command=self.abrir_archivo).pack(side='left', padx=(0, 8))
        ttk.Button(btns, text='💾 Guardar', command=self.guardar_archivo).pack(side='left', padx=(0, 8))
        ttk.Button(btns, text='▶ Compilar', command=self.compilar).pack(side='left', padx=(0, 8))
        ttk.Button(btns, text='🧹 Limpiar', command=self.limpiar).pack(side='left', padx=(0, 8))
        ttk.Button(btns, text='📄 Ejemplos', command=self.mostrar_ejemplos).pack(side='left')

        ttk.Label(frm, text='Resultados:').pack(anchor='w', pady=(10, 6))
        self.txt_resultado = scrolledtext.ScrolledText(
            frm,
            wrap='word',
            height=20,
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#d4d4d4'
        )
        self.txt_resultado.pack(fill='both', expand=True)

        # Inicializar números de línea
        self._actualizar_numeros_linea()

    # ======= Manejo de archivo =======
    def abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            title='Abrir archivo',
            filetypes=[('Archivos de texto', '*.txt'), ('Todos los archivos', '*.*')]
        )
        if not ruta:
            return
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
            self.txt_codigo.delete('1.0', 'end')
            self.txt_codigo.insert('1.0', contenido)
            self.archivo_actual = ruta
            self.root.title(f'Compilador Java - Analizador ({ruta})')
            self._actualizar_numeros_linea()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo abrir el archivo:\n{e}')

    def guardar_archivo(self):
        if not self.archivo_actual:
            self.guardar_como()
            return
        try:
            contenido = self.txt_codigo.get('1.0', 'end-1c')
            with open(self.archivo_actual, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo('Guardar', 'Archivo guardado correctamente.')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar el archivo:\n{e}')

    def guardar_como(self):
        ruta = filedialog.asksaveasfilename(
            title='Guardar archivo como',
            defaultextension='.txt',
            filetypes=[('Archivos de texto', '*.txt'), ('Todos los archivos', '*.*')]
        )
        if not ruta:
            return
        try:
            contenido = self.txt_codigo.get('1.0', 'end-1c')
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(contenido)
            self.archivo_actual = ruta
            self.root.title(f'Compilador Java - Analizador ({ruta})')
            messagebox.showinfo('Guardar como', 'Archivo guardado correctamente.')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar el archivo:\n{e}')

    # ======= Números de línea =======
    def _on_vertical_scroll(self, *args):
        self.txt_codigo.yview(*args)
        self._actualizar_numeros_linea()

    def _on_textscroll(self, *args, scrollbar=None):
        if scrollbar:
            scrollbar.set(*args)
        self._actualizar_numeros_linea()

    def _actualizar_numeros_linea(self, event=None):
        # Borrar contenido actual
        self.line_numbers.delete('all')

        # Obtener el índice de la primera y última línea visible
        try:
            first_index = self.txt_codigo.index('@0,0')
        except tk.TclError:
            return

        first_line = int(first_index.split('.')[0])
        # Obtener la altura en píxeles del widget
        height = self.txt_codigo.winfo_height()

        # Recorrer las líneas visibles
        i = 0
        line = first_line
        while True:
            dline = self.txt_codigo.dlineinfo(f'{line}.0')
            if dline is None:
                if i == 0:
                    # No hay texto aún
                    break
                else:
                    # No hay más líneas visibles
                    break
            y = dline[1]
            if y > height:
                break
            self.line_numbers.create_text(
                40, y + 2, anchor='ne',
                text=str(line),
                fill='#858585',
                font=('Consolas', 10)
            )
            line += 1
            i += 1

    # ======= Compilación =======
    def compilar(self):
        codigo = self.txt_codigo.get('1.0', 'end-1c')
        if not codigo.strip():
            messagebox.showinfo('Aviso', 'Ingrese código para analizar.')
            return

        reporte = []

        try:
            # ========== LÉXICO ==========
            try:
                lexico = AnalizadorLexico()
                tokens = lexico.analizar(codigo)
                reporte.append('='*70 + '\n📋 ANÁLISIS LÉXICO\n' + '='*70)

                if tokens:
                    header = f"{'Tipo':20} {'Valor':25} {'Línea':7}"
                    reporte.append(header)
                    reporte.append('-'*70)
                    for t in tokens:
                        tipo = getattr(t, 'tipo', getattr(getattr(t, 'tipo', None), 'name', str(t)))
                        valor = getattr(t, 'valor', '')
                        linea = getattr(t, 'linea', '')
                        reporte.append(f"{str(tipo):20} {str(valor):25} {str(linea):7}")
                    reporte.append('='*70 + f"\nTotal de tokens: {len(tokens)}\n" + '='*70)
                else:
                    reporte.append('Sin tokens.')
            except Exception as e:
                reporte.append(f'Error léxico: {e}')
                self._mostrar_reporte(reporte)
                return

            # ========== SINTÁCTICO ==========
            ok_sint = False
            try:
                parser = AnalizadorSintactico(tokens)
                ok_sint = parser.analizar() if hasattr(parser, 'analizar') else True
                if hasattr(parser, 'obtener_reporte'):
                    rep_sint = parser.obtener_reporte()
                else:
                    rep_sint = '✅ Sin errores sintácticos' if ok_sint else '❌ Errores sintácticos detectados'
                reporte.append('\n' + '='*70 + '\n🔍 ANÁLISIS SINTÁCTICO\n' + '='*70)
                reporte.append(rep_sint)
            except Exception as e:
                ok_sint = False
                reporte.append(f'Error sintáctico (excepción): {e}')

            # ========== SEMÁNTICO ==========
            ok_sem = False
            try:
                sem = AnalizadorSemantico(tokens)
                ok_sem = sem.analizar() if hasattr(sem, 'analizar') else True
                if hasattr(sem, 'obtener_reporte'):
                    rep_sem = sem.obtener_reporte()
                else:
                    rep_sem = '✅ Semántica correcta' if ok_sem else '❌ Errores semánticos'
                reporte.append(rep_sem)
            except Exception as e:
                ok_sem = False
                reporte.append(f'Error semántico (excepción): {e}')

            # Resumen final
            reporte.append('='*70)
            if ok_sint and ok_sem:
                reporte.append('✅ ANÁLISIS COMPLETO EXITOSO')
            else:
                reporte.append('❌ SE DETECTARON ERRORES EN EL CÓDIGO')
            reporte.append('='*70)

        except Exception as e:
            # Cualquier error inesperado (para que no se cuelgue la GUI)
            reporte.append('\n' + '='*70)
            reporte.append(f'❌ Error inesperado en la compilación: {e}')
            reporte.append('='*70)

        self._mostrar_reporte(reporte)

    def limpiar(self):
        self.txt_codigo.delete('1.0', 'end')
        self.txt_resultado.delete('1.0', 'end')
        self.archivo_actual = None
        self.root.title('Compilador Java - Analizador')
        self._actualizar_numeros_linea()

    def mostrar_ejemplos(self):
        win = tk.Toplevel(self.root)
        win.title('Ejemplos')
        win.geometry('900x600')
        win.configure(bg='#1e1e1e')

        # Diccionario de ejemplos con título → código
        ejemplos = {
            '✅ FOR con IF anidado - Correcto': '''int x = 0;
int cout = 0;
for( x = 0; x < 5; x++ ){
    if(x == 1){
        cout = x;
    }
}''',
            '❌ FOR - Sin punto y coma en el cuerpo': '''int x = 0;
int cout = 0;
for( x = 0; x < 5; x++ ){
    if(x == 1){
        cout = x
    }
}''',
            '❌ FOR - Falta llave de cierre en FOR': '''int x = 0;
for( x = 0; x < 5; x++ ){
    if(x == 1){
        int cout = x;
    }''',
            '❌ FOR - Sin llaves en IF': '''int x = 0;
for( x = 0; x < 5; x++ ){
    if(x == 1)
        int cout = x;
}''',
            '✅ WHILE con IF anidado - Correcto': '''int a = 0;
while( a < 5 ){
    if( a == 2 ){
        a = a + 1;
    }
    a = a + 1;
}''',
            '❌ WHILE - Sin punto y coma en el cuerpo': '''int a = 0;
while( a < 5 ){
    a = a + 1
}''',
            '❌ Semántico - Variable no declarada': '''for( i = 0; i < 10; i++ ){
    int x = i;
}''',
            '✅ DO-WHILE - Correcto': '''int x = 0;
do {
    x = x + 1;
} while (x < 5);''',
            '❌ DO-WHILE - Sin punto y coma final': '''int x = 0;
do {
    x = x + 1;
} while (x < 5)''',
            '✅ Arreglo tamaño fijo + while': '''int arreglo[10];
int x = 0;

while(x < 10){
    arreglo[x] = x * 2;
    x = x + 1;
}''',
            '✅ BubbleSort con for anidado': '''int n = 5;
int numeros[5];
int i = 0;
int j = 0;
int temp = 0;

numeros[0] = 5;
numeros[1] = 1;
numeros[2] = 4;
numeros[3] = 2;
numeros[4] = 3;

for(i = 0; i < n - 1; i++){
    for(j = 0; j < n - 1 - i; j++){
        if(numeros[j] > numeros[j + 1]){
            temp = numeros[j];
            numeros[j] = numeros[j + 1];
            numeros[j + 1] = temp;
        }
    }
}''',
            '✅ String con comillas dobles - Correcto': '''String nombre = "Hola Mundo";
String saludo = "Bienvenido";''',
            '❌ Tipo incompatible - int = String': '''int numero = 10;
numero = "texto";''',
            '❌ Tipo incompatible - String = int': '''String texto = "hola";
texto = 123;''',
            '❌ Tipo incompatible - boolean = int': '''boolean flag = true;
flag = 5;''',
            '❌ Tipo incompatible - int = boolean': '''int x = 0;
x = true;''',
            '✅ Concatenación de String - Correcto': '''String a = "Hola";
String b = "Mundo";
String c = a;''',
            '❌ Operación aritmética con String': '''String texto = "hola";
int x = 5;
int resultado = x - texto;''',
            '❌ Comparación inválida String < int': '''String texto = "hola";
int x = 5;
boolean r = texto < x;''',
            '✅ FOR anidado doble': '''int i = 0;
int j = 0;

for(i = 0; i < 5; i++){
    for(j = 0; j < 3; j++){
        int x = i + j;
    }
}''',
            '✅ WHILE anidado doble': '''int a = 0;
int b = 0;

while(a < 5){
    while(b < 3){
        b = b + 1;
    }
    a = a + 1;
    b = 0;
}''',
            '✅ FOR dentro de WHILE': '''int i = 0;
int j = 0;

while(i < 5){
    for(j = 0; j < 3; j++){
        int x = i * j;
    }
    i = i + 1;
}''',
            '✅ WHILE dentro de FOR': '''int i = 0;
int j = 0;

for(i = 0; i < 5; i++){
    j = 0;
    while(j < 3){
        int x = i + j;
        j = j + 1;
    }
}''',
            '✅ Triple anidamiento FOR': '''int i = 0;
int j = 0;
int k = 0;

for(i = 0; i < 3; i++){
    for(j = 0; j < 3; j++){
        for(k = 0; k < 3; k++){
            int suma = i + j + k;
        }
    }
}''',
            '✅ DO-WHILE dentro de FOR': '''int i = 0;
int j = 0;

for(i = 0; i < 5; i++){
    j = 0;
    do {
        j = j + 1;
    } while(j < 3);
}''',
            '✅ Matriz con FOR anidado': '''int matriz[3];
int i = 0;
int j = 0;

for(i = 0; i < 3; i++){
    for(j = 0; j < 3; j++){
        matriz[i] = i * 3 + j;
    }
}'''
        }

        # Marco principal
        frame = ttk.Frame(win)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Lista de botones de ejemplos a la izquierda
        lista_frame = ttk.Frame(frame)
        lista_frame.pack(side='left', fill='y', padx=(0, 10))

        ttk.Label(lista_frame, text='Ejemplos:', foreground='#d4d4d4').pack(anchor='w', pady=(0, 5))

        # Contenedor scrollable de botones
        canvas = tk.Canvas(lista_frame, bg='#1e1e1e', highlightthickness=0, width=320)
        scroll = ttk.Scrollbar(lista_frame, orient='vertical', command=canvas.yview)
        botones_frame = tk.Frame(canvas, bg='#1e1e1e')

        botones_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=botones_frame, anchor='nw')
        canvas.configure(yscrollcommand=scroll.set)

        canvas.pack(side='left', fill='y', expand=True)
        scroll.pack(side='right', fill='y')

        # Cuadro donde se ve el código del ejemplo
        editor_frame = ttk.Frame(frame)
        editor_frame.pack(side='left', fill='both', expand=True)

        txt_preview = scrolledtext.ScrolledText(
            editor_frame,
            width=60,
            height=25,
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='#d4d4d4'
        )
        txt_preview.pack(fill='both', expand=True)

        def cargar_en_preview(codigo):
            txt_preview.delete('1.0', 'end')
            txt_preview.insert('1.0', codigo)

        def usar_en_editor():
            codigo = txt_preview.get('1.0', 'end-1c')
            self.cargar_ejemplo(codigo)
            win.destroy()

        # Crear un botón por ejemplo con colores
        for nombre, codigo in ejemplos.items():
            # Determinar si es correcto o incorrecto
            es_correcto = nombre.startswith('✅')
            
            # Crear botón con tk.Button para poder usar colores directamente
            if es_correcto:
                btn = tk.Button(
                    botones_frame,
                    text=nombre,
                    command=lambda c=codigo: cargar_en_preview(c),
                    bg='#2e7d32',  # Verde oscuro
                    fg='white',
                    activebackground='#4caf50',  # Verde claro al hover
                    activeforeground='white',
                    font=('Segoe UI', 9, 'bold'),
                    relief='flat',
                    cursor='hand2',
                    anchor='w',
                    padx=10,
                    pady=5
                )
            else:
                btn = tk.Button(
                    botones_frame,
                    text=nombre,
                    command=lambda c=codigo: cargar_en_preview(c),
                    bg='#c62828',  # Rojo oscuro
                    fg='white',
                    activebackground='#ef5350',  # Rojo claro al hover
                    activeforeground='white',
                    font=('Segoe UI', 9, 'bold'),
                    relief='flat',
                    cursor='hand2',
                    anchor='w',
                    padx=10,
                    pady=5
                )
            
            btn.pack(fill='x', pady=2, padx=2)

        # Cargar el primero por defecto
        if ejemplos:
            primer_codigo = next(iter(ejemplos.values()))
            cargar_en_preview(primer_codigo)

        # Botón para enviar el ejemplo al editor principal
        btn_usar = tk.Button(
            editor_frame,
            text='📥 Usar en editor principal',
            command=usar_en_editor,
            bg='#0e639c',
            fg='white',
            activebackground='#1177bb',
            activeforeground='white',
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=15,
            pady=8
        )
        btn_usar.pack(pady=10)

    def cargar_ejemplo(self, codigo):
        self.txt_codigo.delete('1.0', 'end')
        self.txt_codigo.insert('1.0', codigo)
        self._actualizar_numeros_linea()

    def _mostrar_reporte(self, partes):
        self.txt_resultado.delete('1.0', 'end')
        self.txt_resultado.insert('1.0', '\n'.join(partes))


def main():
    root = tk.Tk()
    CompiladorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()