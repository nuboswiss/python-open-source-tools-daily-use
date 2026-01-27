import tkinter as tk
from tkinter import scrolledtext
from collections import deque

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager - Last 10 Items")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Store last 10 clipboard items
        self.clipboard_history = deque(maxlen=10)
        self.last_clipboard = ""
        self.always_on_top = False
        
        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Clipboard History (Last 10 Items)", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Listbox with scrollbar
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                       font=("Courier", 10), height=12)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Bind double-click to copy back to clipboard
        self.listbox.bind('<Double-Button-1>', self.on_item_double_click)
        
        # Preview text area
        preview_label = tk.Label(main_frame, text="Preview (double-click to copy to clipboard):", 
                                font=("Arial", 9))
        preview_label.pack(pady=(0, 5), anchor=tk.W)
        
        self.preview_text = scrolledtext.ScrolledText(main_frame, height=8, wrap=tk.WORD, 
                                                      font=("Courier", 9))
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Bind selection change
        self.listbox.bind('<<ListboxSelect>>', self.on_selection_change)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        copy_btn = tk.Button(button_frame, text="Copy Selected", 
                            command=self.copy_selected, bg="green", fg="black", 
                            padx=10, pady=5, font=("Arial", 10))
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = tk.Button(button_frame, text="Clear History", 
                             command=self.clear_history, bg="red", fg="black",
                             padx=10, pady=5, font=("Arial", 10))
        clear_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        current_btn = tk.Button(button_frame, text="Current Clipboard", 
                               command=self.show_current, bg="blue", fg="black",
                               padx=10, pady=5, font=("Arial", 10))
        current_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.top_btn = tk.Button(button_frame, text="📌 On Top", 
                                command=self.toggle_on_top, bg="yellow", fg="black",
                                padx=10, pady=5, font=("Arial", 10))
        self.top_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_label = tk.Label(main_frame, text="Monitoring clipboard...", 
                                    font=("Arial", 8), fg="green")
        self.status_label.pack(pady=(5, 0), anchor=tk.W)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start clipboard monitoring
        self.monitor_clipboard()
    
    def monitor_clipboard(self):
        """Monitor clipboard for changes using tkinter"""
        try:
            current = self.root.clipboard_get()
            
            # Check if clipboard changed and is not empty
            if current != self.last_clipboard and current.strip():
                self.last_clipboard = current
                self.clipboard_history.appendleft(current)
                self.update_listbox()
        except Exception:
            # Clipboard access failed, continue silently
            pass
        
        # Schedule next check (every 500ms)
        self.root.after(500, self.monitor_clipboard)
    
    def update_listbox(self):
        """Update listbox with history"""
        self.listbox.delete(0, tk.END)
        for idx, item in enumerate(self.clipboard_history, 1):
            # Truncate long items for display
            display_text = item.replace('\n', ' ')[:80]
            if len(item) > 80:
                display_text += "..."
            self.listbox.insert(tk.END, f"{idx}. {display_text}")
    
    def on_selection_change(self, event):
        """Show preview of selected item"""
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            item = list(self.clipboard_history)[idx]
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, item)
            self.preview_text.config(state=tk.DISABLED)
    
    def on_item_double_click(self, event):
        """Copy selected item back to clipboard on double-click"""
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            item = list(self.clipboard_history)[idx]
            self.root.clipboard_clear()
            self.root.clipboard_append(item)
            self.root.update()
            self.status_label.config(text="✓ Copied to clipboard!", fg="green")
            self.root.after(2000, lambda: self.status_label.config(text="Monitoring clipboard..."))
    
    def copy_selected(self):
        """Copy selected item to clipboard"""
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            item = list(self.clipboard_history)[idx]
            self.root.clipboard_clear()
            self.root.clipboard_append(item)
            self.root.update()
            self.status_label.config(text="✓ Copied to clipboard!", fg="green")
            self.root.after(2000, lambda: self.status_label.config(text="Monitoring clipboard..."))
    
    def show_current(self):
        """Show current clipboard content"""
        try:
            current = self.root.clipboard_get()
        except Exception:
            current = "(Unable to access clipboard)"
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, current)
        self.preview_text.config(state=tk.DISABLED)
        self.status_label.config(text="Showing current clipboard content", fg="blue")
    
    def clear_history(self):
        """Clear clipboard history"""
        self.clipboard_history.clear()
        self.update_listbox()
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.config(state=tk.DISABLED)
        self.status_label.config(text="History cleared", fg="orange")
        self.root.after(2000, lambda: self.status_label.config(text="Monitoring clipboard..."))
    
    def toggle_on_top(self):
        """Toggle always on top"""
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        
        if self.always_on_top:
            self.top_btn.config(bg="orange")
            self.status_label.config(text="✓ Always on top enabled", fg="green")
        else:
            self.top_btn.config(bg="yellow")
            self.status_label.config(text="✓ Always on top disabled", fg="green")
        
        self.root.after(2000, lambda: self.status_label.config(text="Monitoring clipboard..."))
    
    def on_closing(self):
        """Handle window close"""
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()