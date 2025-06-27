import tkinter as tk
from tkinter import ttk
import tkfontawesome as tkfa

root = tk.Tk()
root.title("Font Awesome Icons - Método Correcto")
root.geometry("400x500")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill='both', expand=True)

ttk.Label(main_frame, text="Font Awesome Icons", 
          font=('Arial', 16, 'bold')).pack(pady=(0, 20))

try:
    # Método correcto: convertir iconos a imágenes
    
    # Crear iconos como imágenes
    gym_icon = tkfa.icon_to_image("dumbbell", scale_to_width=20)
    user_icon = tkfa.icon_to_image("user", scale_to_width=20)
    money_icon = tkfa.icon_to_image("dollar-sign", scale_to_width=20)
    chart_icon = tkfa.icon_to_image("chart-bar", scale_to_width=20)
    
    # Usar los iconos en labels
    ttk.Label(main_frame, image=gym_icon, text=" Gimnasio", compound='left').pack(pady=5)
    ttk.Label(main_frame, image=user_icon, text=" Usuarios", compound='left').pack(pady=5)
    ttk.Label(main_frame, image=money_icon, text=" Pagos", compound='left').pack(pady=5)
    ttk.Label(main_frame, image=chart_icon, text=" Reportes", compound='left').pack(pady=5)
    
    # Mantener referencias para evitar garbage collection
    root.gym_icon = gym_icon
    root.user_icon = user_icon
    root.money_icon = money_icon
    root.chart_icon = chart_icon
    
except Exception as e:
    ttk.Label(main_frame, text=f"Error: {e}").pack()

root.mainloop()