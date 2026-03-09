import customtkinter as ctk
import struct
import os
import sys
import json
ctk.set_default_color_theme("blue")


class CTkToolTip(ctk.CTkToplevel):
    def __init__(self, widget, message):
        super().__init__()
        self.widget = widget
        self.message = message
        self.withdraw()
        self.overrideredirect(True)
        
        self.lbl = ctk.CTkLabel(self, text=message, fg_color=("white", "#333333"), text_color=("black", "white"), corner_radius=6)
        self.lbl.pack(padx=10, pady=5)
        
        self.widget.bind("<Enter>", self.show)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<Button-1>", self.show)

    def show(self, event=None):
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + 35
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.attributes("-topmost", True)

    def hide(self, event=None):
        self.withdraw()

class BitMasterGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BitMaster Pro - System Engineer Tool")
        self.geometry("900x800+100+0") 

        # -- Theme Persistence Setup --
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.config_file = os.path.join(self.base_dir, "config.json")
        self.load_config()

        # --- Header (Logo + Title + Toggle) ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=10, padx=20, fill="x")

        # Logo: "bos" styled text (Adaptive Colors)
        self.logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.logo_frame.pack(side="left")
        
        self.logo_font = ("Arial", 36, "bold")
        sub_font = ("Arial", 8, "bold")
        
        # Save labels to update color later
        self.lbl_b = ctk.CTkLabel(self.logo_frame, text="b", font=self.logo_font)
        self.lbl_b.grid(row=0, column=0, padx=0)
        self.lbl_o = ctk.CTkLabel(self.logo_frame, text="o", font=self.logo_font)
        self.lbl_o.grid(row=0, column=1, padx=0)
        self.lbl_s = ctk.CTkLabel(self.logo_frame, text="s", font=self.logo_font)
        self.lbl_s.grid(row=0, column=2, padx=0)
        
        self.lbl_sub = ctk.CTkLabel(self.logo_frame, text="SEMICONDUCTORS", font=sub_font)
        self.lbl_sub.grid(row=1, column=0, columnspan=3, pady=0)

        # Theme Toggle
        self.theme_switch = ctk.CTkSwitch(self.header_frame, text="Dark Mode", command=self.toggle_theme)
        
        is_dark = (self.app_config.get("theme", "dark") == "dark")
        if is_dark:
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
            
        self.theme_switch.pack(side="right")
        
        # Apply initial logo colors
        self.update_logo_colors(dark_mode=is_dark)
        
        # Set Appearance Mode
        ctk.set_appearance_mode("dark" if is_dark else "light")

        # Shortcuts Binding & Help
        self.bind("<Control-f>", lambda e: self.focus_main())
        self.bind("<Control-s>", lambda e: self.focus_quick_set())
        self.bind("<Control-r>", lambda e: self.reset_value())
        
        # Shortcut Help Button
        # Shortcut Help Button
        self.btn_help = ctk.CTkButton(self.header_frame, text="?", width=30)
        self.btn_help.pack(side="right", padx=10)
        
        shortcut_msg = "Shortcuts:\nCtrl+F: Main Input\nCtrl+S: Quick Set\nCtrl+R: Reset"
        self.tooltip = CTkToolTip(self.btn_help, shortcut_msg)

        # --- Main Input (Unified with History) ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=20, fill="x")

        # Label + Help Hint
        top_input_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        top_input_frame.pack(fill="x", padx=10, pady=(5,0))
        
        ctk.CTkLabel(top_input_frame, text="Expression / Value:", font=("Arial", 14, "bold")).pack(side="left")
        ctk.CTkLabel(top_input_frame, text="(Supports: +, -, *, /, <<, >>, &, |, ^, ~, 0x, 0b)", font=("Arial", 11, "italic"), text_color="gray").pack(side="left", padx=10)
        
        # ComboBox for History
        self.history_list = []
        self.entry_val = ctk.CTkComboBox(self.input_frame, height=50, font=("Consolas", 20), 
                                         values=self.history_list)
        self.entry_val.pack(fill="x", padx=10, pady=5)
        self.entry_val.set("") 
        
        # Bindings for ComboBox
        self.entry_val._entry.bind("<Return>", self.on_enter_pressed)
        self.entry_val._entry.bind("<KeyRelease>", self.update_all)

        # --- Settings (Width & Endianness) ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.pack(pady=0, padx=20, fill="x")
        
        ctk.CTkLabel(self.settings_frame, text="Data Width:").pack(side="left", padx=5)
        self.width_var = ctk.StringVar(value="32")
        self.seg_width = ctk.CTkSegmentedButton(self.settings_frame, values=["8", "16", "32", "64"], 
                                                variable=self.width_var, command=self.update_all)
        self.seg_width.pack(side="left", padx=5)

        self.btn_endian = ctk.CTkButton(self.settings_frame, text="Swap Endian", command=self.swap_endian, width=120)
        self.btn_endian.pack(side="right", padx=5)

        # --- Results (Stacked Vertically) ---
        self.res_frame = ctk.CTkFrame(self)
        self.res_frame.pack(pady=10, padx=20, fill="x")

        # DEC
        self.res_dec_frame = ctk.CTkFrame(self.res_frame, fg_color="transparent")
        self.res_dec_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.res_dec_frame, text="Decimal:", width=80, anchor="w", font=("Arial", 12)).pack(side="left")
        self.res_dec = ctk.CTkEntry(self.res_dec_frame, font=("Consolas", 16), fg_color="transparent", border_width=0)
        self.res_dec.pack(side="left", fill="x", expand=True)
        self.res_dec.insert(0, "0")
        self.res_dec.configure(state="readonly")

        # HEX
        self.res_hex_frame = ctk.CTkFrame(self.res_frame, fg_color="transparent")
        self.res_hex_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.res_hex_frame, text="Hex:", width=80, anchor="w", font=("Arial", 12)).pack(side="left")
        self.res_hex = ctk.CTkEntry(self.res_hex_frame, font=("Consolas", 16), fg_color="transparent", border_width=0)
        self.res_hex.pack(side="left", fill="x", expand=True)
        self.res_hex.insert(0, "0x0")
        self.res_hex.configure(state="readonly")

        # BIN
        self.res_bin_frame = ctk.CTkFrame(self.res_frame, fg_color="transparent")
        self.res_bin_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.res_bin_frame, text="Binary:", width=80, anchor="w", font=("Arial", 12)).pack(side="left")
        self.res_bin = ctk.CTkEntry(self.res_bin_frame, font=("Consolas", 16), fg_color="transparent", border_width=0)
        self.res_bin.pack(side="left", fill="x", expand=True)
        self.res_bin.insert(0, "0b0")
        self.res_bin.configure(state="readonly")

        # --- Advanced Info ---
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(pady=5, padx=20, fill="x")
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.info_frame.grid_columnconfigure(2, weight=1)

        self.res_signed = ctk.CTkLabel(self.info_frame, text="Signed: 0", font=("Consolas", 14), text_color="gray")
        self.res_signed.grid(row=0, column=0, pady=5)
        self.res_float = ctk.CTkLabel(self.info_frame, text="Float: 0.0", font=("Consolas", 14), text_color="gray")
        self.res_float.grid(row=0, column=1, pady=5)
        self.res_ascii = ctk.CTkLabel(self.info_frame, text="ASCII: ....", font=("Consolas", 14), text_color="gray")
        self.res_ascii.grid(row=0, column=2, pady=5)

        # --- 64-bit Visualizer (Responsive) ---
        # USE PACK with expand=True for the Main Container
        self.bit_frame = ctk.CTkFrame(self)
        self.bit_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Header + Quick Set Bit
        self.bit_header_frame = ctk.CTkFrame(self.bit_frame, fg_color="transparent")
        self.bit_header_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.bit_header_frame, text="Bit Visualizer (63 - 0)", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        
        # Quick Set Input
        self.quick_set_frame = ctk.CTkFrame(self.bit_header_frame, fg_color="transparent")
        self.quick_set_frame.pack(side="right", padx=10)
        ctk.CTkLabel(self.quick_set_frame, text="Quick Toggle Bit:").pack(side="left", padx=5)
        self.quick_set_entry = ctk.CTkEntry(self.quick_set_frame, width=50, placeholder_text="0-63")
        self.quick_set_entry.pack(side="left")
        self.quick_set_entry.bind("<Return>", self.set_bit_from_entry)

        
        self.bit_grid = ctk.CTkFrame(self.bit_frame, fg_color="transparent")
        self.bit_grid.pack(pady=5, fill="both", expand=True)
        
        self.bit_labels = [] # 63 to 0
        
        # 4 Rows of 16 bits
        # Use Grid layout inside each row to allow stretching
        
        for r in range(4):
            start_bit = 63 - (r * 16)
            
            # Row container - Expand horizontally and vertically
            row_frame = ctk.CTkFrame(self.bit_grid, fg_color="transparent")
            row_frame.pack(pady=2, fill="both", expand=True, padx=10)
            
            # Configure columns to stretch evenly
            # 16 chunks + 3 spacers (at 4, 8, 12). 
            # Simplification: Just grid the bits. Use padx for spacing.
            for i in range(16):
                row_frame.grid_columnconfigure(i, weight=1)
            
            for c in range(16):
                bit_idx = start_bit - c
                
                # Column container (Cell)
                # Use grid instead of pack
                # Add extra padx for nibble separators
                pad_r = 1
                if (c + 1) % 4 == 0 and c != 15:
                    pad_r = 10 
                    
                # Index Label
                ctk.CTkLabel(row_frame, text=str(bit_idx), font=("Arial", 10, "bold"), text_color="gray").grid(row=0, column=c, padx=(1, pad_r), pady=0)
                
                # Bit Box (Sticky NSEW to stretch)
                lbl = ctk.CTkLabel(row_frame, text="0", fg_color="#444444", corner_radius=6, font=("Arial", 14, "bold"))
                lbl.grid(row=1, column=c, padx=(1, pad_r), pady=2, sticky="nsew")
                
                # Bind Click to Toggle
                lbl.bind("<Button-1>", lambda e, b=bit_idx: self.on_bit_click(b))

                
                self.bit_labels.append(lbl)
                
            # Allow row 1 (the bits) to expand vertically
            row_frame.grid_rowconfigure(1, weight=1)
            
        # --- Bit Field Extract ---
        # --- Bit Field Extract ---
        # --- Bit Field Extract ---
        self.field_frame = ctk.CTkFrame(self)
        self.field_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.field_frame, text="Extract Bits [End : Start]:").pack(side="left", padx=10)
        self.start_bit = ctk.CTkEntry(self.field_frame, width=50, placeholder_text="0")
        self.start_bit.pack(side="left", padx=5)
        ctk.CTkLabel(self.field_frame, text=":").pack(side="left")
        self.end_bit = ctk.CTkEntry(self.field_frame, width=50, placeholder_text="7")
        self.end_bit.pack(side="left", padx=5)
        
        ctk.CTkButton(self.field_frame, text="Extract", command=self.extract_field, width=80).pack(side="left", padx=10)
        
        # Result as read-only Entry on same line
        self.res_field = ctk.CTkEntry(self.field_frame, width=250, font=("Consolas", 14, "bold"), fg_color="transparent", border_width=0)
        self.res_field.pack(side="left", padx=10, fill="x", expand=True)
        self.res_field.insert(0, "Result: -")
        self.res_field.configure(state="readonly")

    def toggle_theme(self):
        is_dark = (self.theme_switch.get() == 1)
        if is_dark:
            ctk.set_appearance_mode("dark")
            self.app_config["theme"] = "dark"
        else:
            ctk.set_appearance_mode("light")
            self.app_config["theme"] = "light"
        
        self.update_logo_colors(is_dark)
        self.save_config()

    def load_config(self):
        self.app_config = {"theme": "dark"} # Defaults
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.app_config.update(data)
        except Exception:
            pass
            
    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.app_config, f)
        except Exception:
            pass

    def update_logo_colors(self, dark_mode):
        if dark_mode:
            self.lbl_b.configure(text_color="#82B1FF")
            self.lbl_o.configure(text_color="#FF8A80")
            self.lbl_s.configure(text_color="#B9F6CA")
            self.lbl_sub.configure(text_color="#82B1FF")
        else:
            self.lbl_b.configure(text_color="#1a237e")
            self.lbl_o.configure(text_color="#b71c1c")
            self.lbl_s.configure(text_color="#1b5e20")
            self.lbl_sub.configure(text_color="#1a237e")

    def on_enter_pressed(self, event):
        current_text = self.entry_val.get().strip()
        if current_text and current_text not in self.history_list:
            self.history_list.insert(0, current_text)
            if len(self.history_list) > 20: self.history_list.pop()
            self.entry_val.configure(values=self.history_list)
        self.update_all()

    def get_input_val(self):
        raw = self.entry_val.get().strip()
        if not raw: return 0
        try:
            val = eval(raw, {"__builtins__": None}, {})
            if not isinstance(val, int):
                val = int(val)
            width = int(self.width_var.get())
            mask = (1 << width) - 1
            return val & mask
        except Exception as e:
            return None

    def swap_endian(self):
        val = self.get_input_val()
        if val is None: return
        width = int(self.width_var.get())
        num_bytes = width // 8
        try:
            b = val.to_bytes(num_bytes, 'little')
            new_val = int.from_bytes(b, 'big')
            self.entry_val.set(hex(new_val))
            self.update_all()
        except: pass

    def update_all(self, event=None):
        val = self.get_input_val()
        if val is None: return 
        width = int(self.width_var.get())
        
        # Check Appearance Mode for Colors
        mode = ctk.get_appearance_mode()
        is_dark = (mode == "Dark")
        
        # Colors
        color_on = "#00ADB5" # Cyan
        color_off = "#444444" if is_dark else "#E0E0E0" # Grey vs Light Grey
        color_dim = "#222222" if is_dark else "#CCCCCC" # Unused bits

        
        self.set_entry_text(self.res_dec, f"{val}")
        self.set_entry_text(self.res_hex, f"0x{val:X}")
        self.set_entry_text(self.res_bin, f"0b{val:b}")

        # Signed
        mask = 1 << width
        if val >= (1 << (width - 1)):
            signed_val = val - mask
        else:
            signed_val = val
        self.res_signed.configure(text=f"Signed: {signed_val}")

        # Float
        float_str = "-"
        try:
            if width == 32:
                float_str = f"{struct.unpack('f', struct.pack('I', val))[0]:.4e}"
            elif width == 64:
                float_str = f"{struct.unpack('d', struct.pack('Q', val))[0]:.4e}"
        except: pass
        self.res_float.configure(text=f"Float: {float_str}")

        # ASCII
        ascii_str = ""
        try:
            num_bytes = width // 8
            b_arr = val.to_bytes(num_bytes, 'big') 
            for b in b_arr:
                if 32 <= b <= 126: ascii_str += chr(b)
                elif b == 0: ascii_str += "." 
                else: ascii_str += "."
        except: ascii_str = "Err"
        self.res_ascii.configure(text=f"ASCII: {ascii_str}")

        # Visualizer
        bit_str = f"{val:064b}" 
        for i in range(64):
            bit_char = bit_str[i]
            is_active = (bit_char == '1')
            
            is_active = (bit_char == '1')
            
            color = color_on if is_active else color_off
            
            current_bit_pos = 63 - i
            if current_bit_pos >= width:
                color = color_dim
            
            # Text color for Light Mode visibility
            text_col = "white" if is_dark or is_active else "black"
            
            self.bit_labels[i].configure(text=bit_char, fg_color=color, text_color=text_col)

    def on_bit_click(self, bit_index):
        val = self.get_input_val()
        if val is None: val = 0
        
        # Toggle bit
        new_val = val ^ (1 << bit_index)
        
        # Update Main Input
        self.entry_val.set(hex(new_val))
        self.update_all()

    def set_bit_from_entry(self, event):
        try:
            bit_idx = int(self.quick_set_entry.get())
            if 0 <= bit_idx <= 63:
                val = self.get_input_val() or 0
                new_val = val ^ (1 << bit_idx)
                self.entry_val.set(hex(new_val))
                self.update_all()
                self.quick_set_entry.delete(0, 'end')
        except: pass

    def focus_main(self):
        self.entry_val.focus_set()

    def focus_quick_set(self):
        self.quick_set_entry.focus_set()

    def reset_value(self):
        self.entry_val.set("0")
        self.update_all()

    def show_shortcuts_help(self):
        msg = "Keyboard Shortcuts:\n\n" \
              "Ctrl + F : Focus Main Input\n" \
              "Ctrl + S : Focus 'Quick Toggle Bit'\n" \
              "Ctrl + R : Reset Value to 0"
        
        # Simple Toplevel or MessageBox
        top = ctk.CTkToplevel(self)
        top.title("Shortcuts")
        top.geometry("300x200")
        ctk.CTkLabel(top, text=msg, font=("Consolas", 14), padx=20, pady=20).pack()

    def set_entry_text(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.configure(state="readonly")

    def extract_field(self):
        try:
            val = self.get_input_val()
            if val is None: return
            s = int(self.start_bit.get())
            e = int(self.end_bit.get())
            if s > e: s, e = e, s
            
            mask = ((1 << (e - s + 1)) - 1)
            result = (val >> s) & mask
            self.set_entry_text(self.res_field, f"DEC: {result}  HEX: 0x{result:X}")
        except:
            self.set_entry_text(self.res_field, "Invalid!")

if __name__ == "__main__":
    app = BitMasterGUI()
    app.mainloop()