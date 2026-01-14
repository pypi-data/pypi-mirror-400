import tkinter as tk
from tkinter import messagebox
import numpy as np
from project.loader import load_model_and_scaler

FEATURES = [
    "b/dw", "dw/tw", "tf/tw", "bf/2tf", "fyw/fyf", "bf/dw",
    "b/tw", "dw/bw", "If/b^3 tw", "EIf", "Aw/Af",
    "theta", "If", "Viscode"
]

def main():
    model, scaler = load_model_and_scaler()

    root = tk.Tk()
    root.title("Vexp Predictor")
    root.geometry("420x650")

    entries = {}

    for feat in FEATURES:
        tk.Label(root, text=feat).pack()
        e = tk.Entry(root)
        e.pack()
        entries[feat] = e

    def predict():
        try:
            values = [float(entries[f].get()) for f in FEATURES]
            X = np.array(values).reshape(1, -1)
            Xs = scaler.transform(X)
            y = model.predict(Xs)[0]
            messagebox.showinfo("Result", f"Vexp = {y:.3f} kN")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Predict", command=predict).pack(pady=15)
    root.mainloop()

if __name__ == "__main__":
    main()
