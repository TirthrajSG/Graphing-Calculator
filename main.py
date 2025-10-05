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
        self.master = master
        self.master.title("Graphing Calculator")
        self.master.geometry("1200x600")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.state('zoomed')


        self.main_frame = Frame(master)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(9):  # Assume 9 rows
            self.main_frame.rowconfigure(i, weight=1, uniform="row")
        for i in range(18):  # Assume 18 columns
            self.main_frame.columnconfigure(i, weight=1, uniform="col")
        
        self.history = []

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

        self.entry = Entry(self.main_frame, font=("Consolas", 20))
        self.entry.bind("<Key>", self.record_history)
        self.entry.focus_set()
        self.entry.grid(row=0,column=0, columnspan = 16, stick="nsew", padx=5,pady=5)

        self.entry_a = Entry(self.main_frame,text="-10", font=("Consolas", 12), justify="center")
        self.entry_a.grid(row=0, column=16, stick="nsew", padx=5, pady=5)
        self.entry_a.insert(0, "-10")

        self.entry_b = Entry(self.main_frame, text="10", font=("Consolas", 12), justify="center")
        self.entry_b.grid(row=0, column=17, stick="nsew", padx=5, pady=5)
        self.entry_b.insert(0, "10")

        self.plot_frame = Frame(self.main_frame)
        self.plot_frame.grid(row=1,column=8, columnspan=10, rowspan=8, sticky='nsew', padx=10, pady=10)
        for i in range(8):  # Assume 3 rows
            self.plot_frame.rowconfigure(i, weight=1, uniform="row")
        for i in range(1):  # Assume 2 columns
            self.plot_frame.columnconfigure(i, weight=1, uniform="col")

        self.label = Label(self.plot_frame,text="Hello World",font=("Consolas", 20), 
                           anchor="center", wraplength=600,justify="center")
        self.label.grid(row=0, column=0, stick="nsew", padx=5, pady= 5)

        self.plot_lbl = Label(self.plot_frame, anchor='center', bd=2, relief="solid")
        self.plot_lbl.grid(row=1, column=0, rowspan=7, sticky='nsew', padx=5, pady=5)

        self.add_buttons()

    def add_buttons(self):
        
        for i,row in enumerate(self.btns):
            for j, key in enumerate(row):
                if not key: continue
                btn = Button(self.main_frame, 
                                 text=key,
                                 activebackground ="#A1A1A1",
                                 activeforeground="#000000",
                                 bd=0,
                                 font=("Consolas", 14, "bold"),
                                 bg="#ffffff",
                                 relief="flat",
                                 command=lambda k=key: self.btn_clicked(k)
                                )
                btn.grid(row=i+1, column=j, stick="nsew", padx=2, pady=2)

    
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

        def insert_example(example):
            self.entry.delete(0, END)
            self.entry.insert(0, example)
            help_win.lift()  # bring help window on top

        help_win = Toplevel(self.master)
        help_win.title("Help - Graphing Calculator")
        help_win.geometry("600x600+650+60")
        help_win.resizable(False, False)

        # Scrollable canvas + frame
        canvas = Canvas(help_win)
        scrollbar = Scrollbar(help_win, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling for outer canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Load Markdown file
        md_file = "help.md"
        if not os.path.exists(md_file):
            Label(scrollable_frame, text="help.md not found", fg="red").pack()
            return
        
        with open(md_file, "r", encoding="utf-8") as f:
            md_text = f.read()

        md_text = html_content = f"""
<html>
<head>
<style>
body {{
    font-family: Consolas, monospace;
    font-size: 14px;
    line-height: 1.6;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: normal;
    margin: 10px;
}}
h1, h2, h3, h4 {{
    color: #1e3a8a;
}}
</style>
</head>
<body>
{markdown.markdown(md_text)}
</body>
</html>
"""

        # HTML frame for Markdown content (no internal scrollbar)
        container = Frame(scrollable_frame, width=560, height=1400)
        container.pack(padx=10, pady=10)
        container.pack_propagate(False)

        html_frame = HtmlFrame(container, messages_enabled=False)
        html_frame.pack(fill="both", expand=True, padx=10, pady=10)


        # Remove internal scrollbar and disable internal scrolling
        try:
            html_frame.html.scrollbar.pack_forget()
        except AttributeError:
            pass
        html_frame.html.configure(yscrollcommand=None)

        # Load Markdown content
        html_content = markdown.markdown(md_text)
        html_frame.load_html(html_content)

        # Interactive sections
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
        i, j = 0, 1
        for sec, items in sections.items():
            if i != 4:
                header = Label(scrollable_frame, text=sec, font=("Consolas", 14, "bold"), anchor="w")
                header.pack(anchor="w", pady=(10,0), padx=10)
            if i in [1,5]: 
                for label_text, example in items:
                    btn = Button(scrollable_frame, text=label_text, font=("Consolas", 12),
                                command=lambda ex=example: insert_example(ex))
                    btn.pack(anchor="w", padx=20, pady=2)     
            else:
                row_frame = Frame(scrollable_frame)
                row_frame.pack(anchor="w", padx=20, pady=2)

                for label_text, example in items:
                    btn = Button(row_frame, text=label_text, font=("Consolas", 12),
                                command=lambda ex=example: insert_example(ex))
                    btn.pack(side=LEFT, padx=5)
            i += 1


        # Label(scrollable_frame, text="\nInteractive Examples:", font=("Consolas", 14, "bold")).pack(anchor="w", padx=10, pady=(10,2))


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
            # val = expr.subs(x, 2).evalf()
            # self.label.config(text=f"f(x) = {expr}")
            latex_str = f"$f(x,y) = {sp.latex(self.expr)}$"
            
            fig, ax = plt.subplots()
            ax.text(0.5,0.5, latex_str, fontsize=15, ha='center', va='center')
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
        a, b = float(self.entry_a.get()), float(self.entry_b.get())
        n = int(max((b-a)**2, 400))
        if not hasattr(self, 'expr'):
            messagebox.showerror("Error", "Please evaluate a valid expression first.")
            return
        expr = self.expr
        x, y = sp.symbols('x y')
        
        variable = expr.free_symbols

        try:
            if not variable:
                c = expr
                X = np.linspace(a, b, n)
                Y = [c] * n

                fig, ax = plt.subplots()
                ax.plot(X, Y)
                ax.set_xlabel('x')
                ax.set_ylabel('f(x)')
                ax.set_title('Plot of f(x)')
                
            elif x in variable and not y in variable:
                f = sp.lambdify(x, expr, 'numpy')
                X = np.linspace(a, b, n)
                Y = f(X)
                
                fig, ax = plt.subplots()
                ax.plot(X, Y)
                ax.set_xlabel('x')
                ax.set_ylabel('f(x)')
                ax.set_title('Plot of f(x)')
            elif x in variable and y in variable:
                f = sp.lambdify((x, y), expr, modules=["numpy"])
                X = np.linspace(a, b, n)
                Y = np.linspace(a, b, n)
                X, Y = np.meshgrid(X, Y)
                Z = f(X, Y)
                
                fig, ax = plt.subplots()
                contour = ax.contour(X, Y, Z, levels=[0], colors='blue')  # level=0 for the curve
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.set_title('Contour plot of f(x, y)=0')
            else:
                messagebox.showinfo("Info", "Plotting only supported for expressions with x or x and y.")
                return
            buf2 = BytesIO()
            plt.savefig(buf2, format='png', transparent=True, dpi=100, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            buf2.seek(0)
            
            img = Image.open(buf2)
            img = img.crop(img.getbbox())
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
        add=k
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

root = Tk()
app = App(root)
root.mainloop()