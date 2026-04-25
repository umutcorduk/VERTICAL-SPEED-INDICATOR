import tkinter as tk
import math
import threading
import os

class VSIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vertical Speed Indicator")
        self.root.configure(bg="#151515")
        
        self.width = 500
        self.height = 500
        self.cx = self.width / 2
        self.cy = self.height / 2
        self.r = 210
        
        # Canvas for drawing the instrument
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#151515", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        
        self.target_val = 0.0
        self.current_val = 0.0
        
        self.draw_gauge()
        
        # Center shadow/hole
        self.canvas.create_oval(self.cx-20, self.cy-20, self.cx+20, self.cy+20, fill="#1c1c1c", outline="")
        
        # Pointer
        self.needle = self.canvas.create_line(self.cx, self.cy, self.cx, self.cy, fill="#ffd700", width=4, capstyle=tk.ROUND)
        self.center_cap = self.canvas.create_oval(self.cx-15, self.cy-15, self.cx+15, self.cy+15, fill="#2a2a2a", outline="#000000", width=2)
        
        self.update_needle(0)
        self.animate()

    def val_to_angle(self, v):
        # Sınırlandırma (-6000 ile 6000 arası)
        v = max(-6000, min(6000, v))
        # 0'ın açısı 180 derece (Sol).
        # Her 1000 ft/min 30 dereceye denk gelir (saat yönünde azalması veya artması için).
        return 180 - v * 0.03

    def draw_gauge(self):
        # Dış çerçeve
        self.canvas.create_oval(self.cx-self.r-15, self.cy-self.r-15, self.cx+self.r+15, self.cy+self.r+15, fill="#1a1a1a", outline="#3a3a3a", width=6)
        
        for v in range(-6000, 6001, 100):
            a = math.radians(self.val_to_angle(v))
            if v % 1000 == 0:
                l = 25
                w = 4
            elif v % 500 == 0:
                l = 15
                w = 2
            else:
                l = 8
                w = 1
                
            color = "#ffffff"
            if v > 5000 or v < -5000:
                color = "#e63946" # Limit üstü için kırmızı bölge çizgileri
                
            x1 = self.cx + (self.r - l) * math.cos(a)
            y1 = self.cy - (self.r - l) * math.sin(a)
            x2 = self.cx + self.r * math.cos(a)
            y2 = self.cy - self.r * math.sin(a)
            
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=w)
            
            # Sayısal metinler (1, 2, 4, 5 vs.)
            if v % 1000 == 0 and abs(v) != 6000 and abs(v) != 3000 and v != 0:
                num = str(abs(v) // 1000)
                nx = self.cx + (self.r - 55) * math.cos(a)
                ny = self.cy - (self.r - 55) * math.sin(a)
                self.canvas.create_text(nx, ny, text=num, fill="white", font=("Arial", 22, "bold"))
                
        # Özel durumlarda yerleştirilen '0' ve '6' değerleri
        self.canvas.create_text(self.cx + (self.r - 55) * math.cos(math.radians(180)), self.cy - (self.r - 55) * math.sin(math.radians(180)), text="0", fill="white", font=("Arial", 22, "bold"))
        self.canvas.create_text(self.cx + (self.r - 55) * math.cos(math.radians(0)), self.cy - (self.r - 55) * math.sin(math.radians(0)), text="6", fill="white", font=("Arial", 22, "bold"))

        # Gsterge üst ve alt metinleri
        self.canvas.create_text(self.cx, self.cy - 100, text="VERTICAL SPEED", fill="white", font=("Arial", 16))
        self.canvas.create_text(self.cx, self.cy + 100, text="FEET/MIN ×1000", fill="white", font=("Arial", 14))
        
        # Kritik alan uyarı yayı (Overspeed arkı)
        # Math koordinatında 330 ile 30 derece arası sırasıyla -5000 ila +5000 aralığını kapsar ve sağa denk gelir
        self.canvas.create_arc(self.cx-self.r+8, self.cy-self.r+8, self.cx+self.r-8, self.cy+self.r-8, start=330, extent=60, style=tk.ARC, outline="#e63946", width=3)

    def update_needle(self, val):
        a = math.radians(self.val_to_angle(val))
        # İbre kuyruğu (ağırlaştırıcı kısım)
        tx = self.cx + 40 * math.cos(a + math.pi)
        ty = self.cy - 40 * math.sin(a + math.pi)
        # İbre ucu
        hx = self.cx + (self.r - 20) * math.cos(a)
        hy = self.cy - (self.r - 20) * math.sin(a)
        
        self.canvas.coords(self.needle, tx, ty, hx, hy)
        self.canvas.tag_raise(self.center_cap)

    def set_target(self, val):
        self.target_val = val

    def animate(self):
        # Yumuşak animasyon efekti (interpolasyon)
        diff = self.target_val - self.current_val
        if abs(diff) > 2:
            self.current_val += diff * 0.08
        else:
            self.current_val = self.target_val
            
        self.update_needle(self.current_val)
        self.root.after(30, self.animate)

def terminal_thread(app):
    """Terminalden değerleri okuyan asenkron fonksiyon"""
    print("====================================")
    print(" Vertical Speed Indicator Simulator ")
    print("====================================")
    print("Terminal üzerinden FPM (Feet Per Minute) değerini girin.")
    print("Tırmanış için pozitif (örn: 1500), alçalış için negatif (örn: -2000) değerler kullanın.")
    print("Çıkmak için 'exit' veya 'q' yazın.\n")
    while True:
        try:
            line = input("VSI (FPM)> ")
            if line.strip().lower() in ['exit', 'quit', 'q']:
                print("Çıkılıyor...")
                os._exit(0)
            
            val = float(line)
            app.set_target(val)
        except ValueError:
            print("Lütfen geçerli bir sayı girin (örn: 1500 veya -500).")
        except EOFError:
            os._exit(0)

def main():
    root = tk.Tk()
    root.geometry("540x540")
    root.resizable(False, False)
    # X ikonuna basıldığında terminal thread'ini de öldürür
    root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
    app = VSIApp(root)
    
    # Terminal dinleyicisini ayrı bir iş parçacığında arka planda başlatıyoruz
    t = threading.Thread(target=terminal_thread, args=(app,), daemon=True)
    t.start()
    
    root.mainloop()

if __name__ == "__main__":
    main()
