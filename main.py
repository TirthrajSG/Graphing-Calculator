from tkinter import *
from tkinter import messagebox
from tkinterweb import HtmlFrame

from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from io import BytesIO
import markdown
import os

import numpy as np
import sympy as sp
from sympy import factorial
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

class App:
    def __init__(self, master):
        # Main Window
        self.master = master
        self.master.title("Graphing Calculator")
        self.master.geometry("1200x600")

        # Themes
        self.themes_func()
        self.theme = self.theme10

        self.master.configure(bg=self.theme["bg"])
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.state('zoomed')
        self.master.iconbitmap("imgs/icon.ico")

        # History Stack for undo
        self.history = []
        self.help_open = False
        
        # Lists of Buttons and Labels
        self.button_widgets = []
        self.button_widgets_help = []
        self.lbl_widgets = []
        self.lbl_widgets_help = []
        self.row_frame_help = []

        # Main Frame
        self.main_frame = Frame(master, bg=self.theme["bg"])
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(9): # 9 rows
            self.main_frame.rowconfigure(i, weight=1, uniform="row")
        for i in range(18): # 18 cols
            self.main_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Button Layout
        self.btns = [
            ["x","y","e","π","(",")", "lcm()", "sign()"],
            ["a**2","a**b","sqrt()","root()","ln()","log()","gcd()","Sum()"],
            ["7","8","9","+","%","<--","abs()","Prod()"],
            ["4","5","6","-","&","!","ceil()","diff()"],
            ["1","2","3","*","^","nCr()","floor()","limit()"],
            [".","0",",","/","//","nPr()","round()","integ()"],
            ["sin()","cos()","tan()","csc()","sec()","cot()", "Clear", "Eval"],
            ["asin()","acos()","atan()","acsc()","asec()","acot()", "Plot", "Help"]
        ]

        # Theme of Entry
        entry_style = {
            "font": ("Consolas", 20),
            "bg": self.theme["entry_bg"],
            "fg": self.theme["fg"],
            "insertbackground": self.theme["fg"], # Cursor color
            "relief": "flat",
            "bd": 5
        }
        self.entry = Entry(self.main_frame, **entry_style)
        self.entry.bind("<Key>", self.record_history) # Store History
        self.entry.focus_set()
        self.entry.grid(row=0,column=0, columnspan = 14, sticky="nsew", padx=5,pady=5)

        # Change Text Size
        entry_ab_style = entry_style.copy()
        entry_ab_style["font"] = ("Consolas", 12)

        self.entry_a = Entry(self.main_frame, text="-10", justify="center", **entry_ab_style)
        self.entry_a.grid(row=0, column=14, stick="nsew", padx=5, pady=5)
        self.entry_a.insert(0, "-10")

        self.entry_b = Entry(self.main_frame, text="10", justify="center", **entry_ab_style)
        self.entry_b.grid(row=0, column=15, stick="nsew", padx=5, pady=5)
        self.entry_b.insert(0, "10")

        # Theme Change Option Menu
        self.theme_var = StringVar(value=self.themes)
        self.theme_var.set("Sepia Tone")
        self.theme_menu = OptionMenu(self.main_frame, self.theme_var, *self.themes.keys(), command=self.change_theme)
        self.theme_menu.config(
            font=("Consolas", 15),
            bg=self.theme["btn_bg"],
            fg=self.theme["fg"],
            activebackground=self.theme["btn_active_bg"],
            activeforeground=self.theme["fg"],
            relief="flat",
            bd=0
        )
        self.theme_menu.grid(row=0, column=16, columnspan=2, stick="nsew", padx=5, pady=5)
        

        # Frame for the plots
        self.plot_frame = Frame(self.main_frame, bg=self.theme["bg"])
        self.plot_frame.grid(row=1,column=8, columnspan=10, rowspan=8, sticky='nsew', padx=10, pady=10)

        # Frame is 8x1
        for i in range(8):
            self.plot_frame.rowconfigure(i, weight=1, uniform="row")
        self.plot_frame.columnconfigure(0, weight=1, uniform="col")

        # Expression Label
        self.label = Label(self.plot_frame,text="Welcome!",
                           font=("Consolas", 20),
                           anchor="center", wraplength=600, justify="center",
                           bg=self.theme["bg"], fg=self.theme["fg"])
        self.label.grid(row=0, column=0, sticky="nsew", padx=5, pady= 5)
        self.lbl_widgets.append(self.label)

        # Plot Label
        self.plot_lbl = Label(self.plot_frame, anchor='center',
                              bg=self.theme["plot_bg"], bd=1, relief="solid", highlightbackground=self.theme["btn_bg"])
        self.plot_lbl.grid(row=1, column=0, rowspan=7, sticky='nsew', padx=5, pady=5)
        self.lbl_widgets.append(self.plot_lbl)
        
        self.add_buttons()
    
    def themes_func(self):
        self.theme1 = {
            "bg": "#282a36",
            "fg": "#f8f8f2",
            "entry_bg": "#282a36",
            "btn_bg": "#44475a",
            "btn_active_bg": "#6272a4",
            "plot_bg": "#282a36",
            "accent_color": "#8be9fd"
        }
        self.theme2 = {
            "bg": "#121212",          # Very dark background (near black)
            "fg": "#EAEAEA",          # Bright white text
            "entry_bg": "#1E1E1E",    # Dark grey for entries
            "btn_bg": "#2D2D2D",      # Lighter grey for buttons
            "btn_active_bg": "#007ACC", # Vibrant blue for active/hover
            "plot_bg": "#1E1E1E",     # Plot background
            "accent_color": "#00BFFF" # Deep sky blue for plots/accents
        }
        self.theme3 = {
            "bg": "#002b36",
            "fg": "#839496",
            "entry_bg": "#073642",
            "btn_bg": "#586e75",
            "btn_active_bg": "#657b83",
            "plot_bg": "#073642",
            "accent_color": "#268bd2"
        }
        self.theme4 = {
            "bg": "#2D2A2E",
            "fg": "#FCFCFA",
            "entry_bg": "#383539",
            "btn_bg": "#4D4A4F",
            "btn_active_bg": "#FF6188",
            "plot_bg": "#2D2A2E",
            "accent_color": "#A9DC76"
        }
        self.theme5 = {
            "bg": "#282828",
            "fg": "#ebdbb2",
            "entry_bg": "#3c3836",
            "btn_bg": "#504945",
            "btn_active_bg": "#665c54",
            "plot_bg": "#3c3836",
            "accent_color": "#fabd2f"
        }
        self.theme6 = {
            "bg": "#0F1C2E",
            "fg": "#A6ACB9",
            "entry_bg": "#1B2A41",
            "btn_bg": "#324A5F",
            "btn_active_bg": "#5C7B9A",
            "plot_bg": "#1B2A41",
            "accent_color": "#33A1FD"
        }
        self.theme7 = {
            "bg": "#2A363B",
            "fg": "#E8E8E8",
            "entry_bg": "#3A464B",
            "btn_bg": "#5A666B",
            "btn_active_bg": "#99B898",
            "plot_bg": "#3A464B",
            "accent_color": "#A8D5BA"
        }
        self.theme8 = {
            "bg": "#fdf6e3",
            "fg": "#657b83",
            "entry_bg": "#eee8d5",
            "btn_bg": "#93a1a1",
            "btn_active_bg": "#839496",
            "plot_bg": "#eee8d5",
            "accent_color": "#268bd2"
        }
        self.theme9 = {
            "bg": "#ffffff",
            "fg": "#24292e",
            "entry_bg": "#fafbfc",
            "btn_bg": "#e1e4e8",
            "btn_active_bg": "#d1d5da",
            "plot_bg": "#fafbfc",
            "accent_color": "#0366d6"
        }
        self.theme10 = {
            "bg": "#F1E9DA",
            "fg": "#5E4A33",
            "entry_bg": "#E6DBCB",
            "btn_bg": "#B9A28B",
            "btn_active_bg": "#9C836A",
            "plot_bg": "#E6DBCB",
            "accent_color": "#8A6B4A"
        }
        self.theme11 = {
            "bg": "#1A1A1A",
            "fg": "#F2F2F2",
            "entry_bg": "#101010",
            "btn_bg": "#4D0000",
            "btn_active_bg": "#800000",
            "plot_bg": "#101010",
            "accent_color": "#FF0000"
        }
        self.themes = {
            "Dracula":self.theme1,
            "Nord Dark":self.theme2,
            "Solarized Dark":self.theme3,
            "Monokai Pro":self.theme4,
            "Gruvbox Dark":self.theme5,
            "Ocean Blue":self.theme6,
            "Matcha Green":self.theme7,
            "Solarized Light":self.theme8,
            "GitHub Light":self.theme9,
            "Sepia Tone":self.theme10,
            "Crimson Red":self.theme11,
        }

    def add_buttons(self):
        for i,row in enumerate(self.btns):
            for j, key in enumerate(row):
                if not key: continue
                
                # Button of in-build Keyboard
                btn = Button(self.main_frame, 
                             text=key,
                             activebackground=self.theme["btn_active_bg"],
                             activeforeground=self.theme["fg"],
                             bg=self.theme["btn_bg"],
                             fg=self.theme["fg"],
                             bd=0,
                             font=("Consolas", 14, "bold"),
                             relief="flat",
                             command=lambda k=key: self.btn_clicked(k)
                            )
                btn.grid(row=i+1, column=j, stick="nsew", padx=2, pady=2)
                self.button_widgets.append(btn)

    def apply_theme_to_all_widgets(self):
        self.master.config(bg=self.theme["bg"])
        self.main_frame.config(bg=self.theme["bg"])
        self.plot_frame.config(bg=self.theme["bg"])

        # For Help Window
        if self.help_open:
            self.help_win.config(bg=self.theme["bg"])
            self.canvas.config(bg=self.theme["bg"])
            self.scrollable_frame.config(bg=self.theme["bg"])
            self.container.config(bg=self.theme["bg"])

            for row_frame in self.row_frame_help:
                row_frame.config(bg=self.theme["bg"])

            for lbl in self.lbl_widgets_help:
                lbl.config(bg=self.theme["bg"], fg=self.theme["fg"])

            for btn in self.button_widgets_help:
                btn.config(activebackground=self.theme["btn_active_bg"], activeforeground=self.theme["fg"],
                        bg=self.theme["btn_bg"], fg=self.theme["fg"])

            self.html_content = f"""
            <html><head><style>
            body {{
                font-family: Consolas, monospace; font-size: 14px;
                line-height: 1.6; background-color: {self.theme['entry_bg']};
                color: {self.theme['fg']}; margin: 20px;
            }}
            h1, h2, h3, h4 {{ color: {self.theme['accent_color']}; }}
            code {{ background-color: {self.theme['btn_bg']}; padding: 2px 4px; border-radius: 4px; }}
            </style></head>
            <body>{markdown.markdown(self.md_text, extensions=['fenced_code'])}</body>
            </html>"""
            self.html_frame.load_html(self.html_content)


        self.theme_menu.config(bg=self.theme["btn_bg"],
                                fg=self.theme["fg"],
                                activebackground=self.theme["btn_active_bg"],
                                activeforeground=self.theme["fg"]
                            )
        

        entry_style = {"font": ("Consolas", 20), "bg": self.theme["entry_bg"], "fg": self.theme["fg"],
                       "insertbackground": self.theme["fg"], "relief": "flat", "bd": 5}
        self.entry.config(**entry_style)

        entry_ab_style = entry_style.copy()
        entry_ab_style["font"] = ("Consolas", 12)
        self.entry_a.config(**entry_ab_style)
        self.entry_b.config(**entry_ab_style)



        for lbl in self.lbl_widgets:
            lbl.config(bg=self.theme["bg"], fg=self.theme["fg"])

        for btn in self.button_widgets:
            btn.config(activebackground=self.theme["btn_active_bg"], activeforeground=self.theme["fg"],
                       bg=self.theme["btn_bg"], fg=self.theme["fg"])

    def change_theme(self, theme_name):

        self.theme_name = theme_name
        self.theme = self.themes[self.theme_name]
        self.apply_theme_to_all_widgets()
        
        # Redraw plots and latex with new theme colors if an expression exists
        if hasattr(self, 'expr'):
            self.eval_expr()
            self.plot_expr()
    
    def nPr(self, n, r):
        return factorial(n) / factorial(n - r)

    def record_history(self, event):
        current = self.entry.get()
        if not self.history or self.history[-1] != current:
            self.history.append(current)

    def undo(self):
        if self.history:
            last_state = self.history.pop()
            self.entry.delete(0, END)
            self.entry.insert(0, last_state)

    def help(self):
        self.help_open = True

        def _on_help_close(event=None):
            self.help_open = False

        def insert_example(example):
            self.entry.delete(0, END)
            self.entry.insert(0, example)
            self.help_win.lift()

        self.help_win = Toplevel(self.master)
        self.help_win.title("Help - Graphing Calculator")
        self.help_win.geometry("600x600+650+60")
        self.help_win.resizable(False, False)
        self.help_win.configure(bg=self.theme["bg"])
        self.help_win.bind("<Destroy>", _on_help_close)

        self.canvas = Canvas(self.help_win, bg=self.theme["bg"], highlightthickness=0)
        scrollbar = Scrollbar(self.help_win, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = Frame(self.canvas, bg=self.theme["bg"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0,0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        md_file = "help.md"
        if not os.path.exists(md_file):
            Label(self.scrollable_frame, text="help.md not found", fg="red", bg=self.theme["bg"]).pack()
            return
        
        with open(md_file, "r", encoding="utf-8") as f:
            self.md_text = f.read()

        self.html_content = f"""
        <html><head><style>
        body {{
            font-family: Consolas, monospace; font-size: 14px;
            line-height: 1.6; background-color: {self.theme['entry_bg']};
            color: {self.theme['fg']}; margin: 20px;
        }}
        h1, h2, h3, h4 {{ color: {self.theme['accent_color']}; }}
        code {{ background-color: {self.theme['btn_bg']}; padding: 2px 4px; border-radius: 4px; }}
        </style></head>
        <body>{markdown.markdown(self.md_text, extensions=['fenced_code'])}</body>
        </html>"""

        self.container = Frame(self.scrollable_frame, width=560, height=1400, bg=self.theme['bg'])
        self.container.pack(padx=10, pady=10)
        self.container.pack_propagate(False)

        self.html_frame = HtmlFrame(self.container, messages_enabled=False)
        self.html_frame.pack(fill="both", expand=True)
        self.html_frame.load_html(self.html_content)
        
        sections = {
            "1. Trigonometry": [
                ("sin(x)", "sin(x)"),
                ("cos(x)", "cos(x)"),
                ("tan(x)", "tan(x)"),
                ("cot(x)", "cot(x)"),
                ("sec(x)", "sec(x)"),
                ("cosec(x)", "cosec(x)")
            ],
            "2. Calculus": [
                ("Sum: Sum(f(i), (i, a, b))", "Sum(i**2, (i, 1, 10))"),
                ("Product: Product(f(i), (i, a, b))", "Product(i**2, (i, 1, 10))"),
                ("Derivative: diff(f(x), x)", "diff(x**2, x)"),
                ("Definite Integration: integrate(f(x), (x,a,b))", "integrate(x**2, (x,0,1))"),
                ("Indefinite Integration: integrate(f(x), x)", "integrate(x**2, x)"),
                ("Limit: limit(f(x), x, a)", "limit(sin(x)/x, x, 0)")
            ],
            "3. Combinatorics": [
                ("nCr(n,r)", "nCr(5,2)"),
                ("nPr(n,r)", "nPr(5,2)"),
                ("Factorial: !", "5!")
            ],
            "4. Number Theory": [
                ("lcm(a,b)", "lcm(4,9)"),
                ("gcd(a,b)", "gcd(4,9)"),
                ("abs(x)", "abs(x)"),
                ("sign(x)", "sign(x)") 
            ],
            "4.5": [
                ("ceiling(x)", "ceiling(x)"),
                ("floor(x)", "floor(x)"),
                ("round(x)", "round(x)")
            ],
            "5. Plotting": [
                ("1D function: x**2 + 2*x + 1", "x**2 + 2*x + 1"),
                ("2D function: x**2 + y**2 - 1", "x**2 + y**2 - 1")
            ]
        }
        i = 0
        for sec, items in sections.items():
            if i != 4:
                header = Label(self.scrollable_frame, bg=self.theme["bg"], fg=self.theme["fg"],text=sec, font=("Consolas", 14, "bold"), anchor="w")
                header.pack(anchor="w", pady=(10,0), padx=10)
                self.lbl_widgets_help.append(header)

            if i in [1,5]: 
                for label_text, example in items:
                    btn = Button(self.scrollable_frame, text=label_text,
                                activebackground=self.theme["btn_active_bg"],
                                activeforeground=self.theme["fg"],
                                bg=self.theme["btn_bg"],
                                fg=self.theme["fg"],
                                bd=0,
                                font=("Consolas", 14, "bold"),
                                relief="flat",
                                command=lambda ex=example: insert_example(ex))
                    btn.pack(anchor="w", padx=20, pady=10)     
                    self.button_widgets_help.append(btn)
            else:
                row_frame = Frame(self.scrollable_frame, bg=self.theme["bg"])
                row_frame.pack(anchor="w", padx=20, pady=2)

                self.row_frame_help.append(row_frame)

                for label_text, example in items:
                    btn = Button(row_frame, text=label_text,
                                activebackground=self.theme["btn_active_bg"],
                                activeforeground=self.theme["fg"],
                                bg=self.theme["btn_bg"],
                                fg=self.theme["fg"],
                                bd=0,
                                font=("Consolas", 14, "bold"),
                                relief="flat",
                                command=lambda ex=example: insert_example(ex))
                    btn.pack(side=LEFT, padx=5, pady=10)
                    self.button_widgets_help.append(btn)
            i += 1

    def eval_expr(self):
        expr_str = self.entry.get()
        
        try:
            transformations = standard_transformations + (implicit_multiplication_application,)
            local_dict = {
                'ceil': sp.ceiling,
                'nPr': self.nPr,
                'nCr':sp.binomial,
                'e': sp.E,           # ensures 'e' is treated as the constant
                'π': sp.pi,
                'sin': sp.sin,
                'cos': sp.cos,
                'tan': sp.tan,
                'cot': sp.cot,
                'sec': sp.sec,
                'csc': sp.csc,
                'ln': sp.ln,
                'sqrt': sp.sqrt
            }
            self.expr = parse_expr(expr_str, transformations=transformations, local_dict=local_dict)
            self.expr = sp.sympify(self.expr)

            if not self.expr.free_symbols:
                self.expr = self.expr.evalf()

            latex_str = f"$f(x,y) = {sp.latex(self.expr)}$"
            
            fig, ax = plt.subplots()
            ax.text(0.5,0.5, latex_str, fontsize=15, ha='center', va='center', color=self.theme["fg"])
            ax.axis('off')
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            buf = BytesIO()
            plt.savefig(buf, format='png',transparent=True, dpi=100, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            buf.seek(0)

            latex_img = Image.open(buf)
            latex_img = latex_img.crop(latex_img.getbbox())
            photo = ImageTk.PhotoImage(latex_img)
            self.label.config(text="", image=photo)
            self.label.image = photo

        except Exception as e:
            messagebox.showerror("Error", f"Invalid function:\n{e}")

    def plot_expr(self):
        try:
            a, b = float(self.entry_a.get()), float(self.entry_b.get())
            n = 500
            if not hasattr(self, 'expr'):
                messagebox.showerror("Error", "Please evaluate a valid expression first.")
                return
            expr = self.expr
            x, y = sp.symbols('x y')
            
            variable = expr.free_symbols
            
            fig, ax = plt.subplots(facecolor=self.theme["plot_bg"])
            ax.set_facecolor(self.theme["plot_bg"])
            
            if not variable: # Constant
                X = np.linspace(a, b, n)
                Y = [float(expr)] * n
                ax.plot(X, Y, color=self.theme["accent_color"])
            
            elif x in variable and y not in variable: # 1D plot
                f = sp.lambdify(x, expr, 'numpy')
                X = np.linspace(a, b, n)
                Y = f(X)
                ax.plot(X, Y, color=self.theme["accent_color"])
            
            elif x in variable and y in variable: # 2D contour plot
                f = sp.lambdify((x, y), expr, "numpy")
                X_vals = np.linspace(a, b, n)
                Y_vals = np.linspace(a, b, n)
                X, Y = np.meshgrid(X_vals, Y_vals)
                Z = f(X, Y)
                ax.contour(X, Y, Z, levels=[0], colors=self.theme["accent_color"])
                ax.set_ylabel('y')
                ax.set_title('Contour plot of f(x, y)=0')
            else:
                messagebox.showinfo("Info", "Plotting only supported for expressions with x or x and y.")
                plt.close(fig)
                return

            # --- Style the plot axes and labels ---
            ax.set_xlabel('x')
            ax.tick_params(axis='x', colors=self.theme["fg"])
            ax.tick_params(axis='y', colors=self.theme["fg"])
            ax.xaxis.label.set_color(self.theme["fg"])
            ax.yaxis.label.set_color(self.theme["fg"])
            ax.title.set_color(self.theme["fg"])
            ax.spines['bottom'].set_color(self.theme["fg"])
            ax.spines['top'].set_color(self.theme["fg"])
            ax.spines['left'].set_color(self.theme["fg"])
            ax.spines['right'].set_color(self.theme["fg"])
            ax.grid(True, color=self.theme["btn_bg"], linestyle='--', linewidth=0.5)


            buf2 = BytesIO()
            plt.savefig(buf2, format='png', facecolor=fig.get_facecolor(), dpi=100, bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            buf2.seek(0)
            
            img = Image.open(buf2)
            photo = ImageTk.PhotoImage(img)
            self.plot_lbl.config(image=photo)
            self.plot_lbl.image = photo
        except Exception as e:
            messagebox.showerror("Plotting Error", f"An error occurred while plotting:\n{e}")

    def btn_clicked(self, k):
        if k == "Eval": self.eval_expr();return
        elif k == "Plot": self.plot_expr();return
        elif k == "Help": self.help();return
        
        i = 1
        add = k
        if k not in ("<--", "Clear"):
            self.history.append(self.entry.get())

        if k == "a**2": add="**2"
        elif k == "a**b": add="**"
        elif k == "log()": add="log(a, b)"; i=4
        elif k == "nCr()": add="nCr(n, r)"; i=4
        elif k == "nPr()": add="nPr(n, r)"; i=4
        elif k == "lcm()": add="lcm(a, b)"; i=4
        elif k == "gcd()": add="gcd(a, b)"; i=4
        elif k == "Sum()": add = "Sum(f(i), (i, a, b))"; i = 12
        elif k == "Prod()": add="Product(f(i), (i, a, b))"; i=12
        elif k == "diff()": add="diff(f(x), x)"; i=4
        elif k == "limit()": add = "limit(f(x), x, a)";i=7
        elif k == "integ()": add="integrate(f(x), (x, a, b))"; i=12
        elif k == "<--": self.undo(); return
        elif k == "Clear": 
            self.history.append(self.entry.get())
            self.entry.delete(0, END)
            return
        
        self.entry.insert(INSERT, add)
        if "(" in k and k.endswith(")"): 
            pos = self.entry.index(INSERT)
            if pos > 0: self.entry.icursor(pos-i)

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()