import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os

# Global variables
FilePath = ""
FileName = ""

# Dictionary to store prices for colored and non-colored printing
prices = {"colored": 4, "non-colored": 2}

class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Viewer")
        self.current_page = 0

        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=True, fill='both')

        self.prev_button = tk.Button(root, text="Previous Page", command=self.prev_page)
        self.prev_button.pack(side='left')

        self.next_button = tk.Button(root, text="Next Page", command=self.next_page)
        self.next_button.pack(side='right')

    def open_pdf(self):
        global FilePath
        if FilePath:
            self.file_path = FilePath
            self.display_pdf(FilePath)
        else:
            messagebox.showinfo("Info", "No file selected")

    def display_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)
            self.num_pages = len(doc)
            self.render_page()
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")

    def render_page(self):
        self.canvas.delete("all")
        page = fitz.open(self.file_path).load_page(self.current_page)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Calculate position to center the image
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_width = img.width
        img_height = img.height
        x_offset = (canvas_width - img_width) // 100
        y_offset = (canvas_height - img_height) // 100

        # Create centered image
        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(x_offset, y_offset, anchor='nw', image=self.img_tk)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()

    def next_page(self):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            self.render_page()


def open_file_explorer():
    global FilePath, FileName
    filename = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if filename:
        print("Selected file:", filename)
        FilePath = filename  # Store the file path in the global variable
        FileName = os.path.basename(filename)  # Extract the file name from the path
        lbl_filename.config(text="File Name: " + FileName)
        calculate_cost()

def open_preview_window():
    global FilePath
    if not FilePath:
        messagebox.showinfo("Info", "No file selected")
    else:
        preview_window = tk.Toplevel(root)
        preview_window.title("Preview Window")
        preview_window.attributes('-fullscreen', True)  # Set fullscreen attribute to True

        pdf_viewer = PDFViewerApp(preview_window)
        pdf_viewer.open_pdf()

        # Create a close button
        btn_close = tk.Button(preview_window, text="Close", command=preview_window.destroy)
        btn_close.pack(side=tk.BOTTOM)



def count_pages(filename):
    try:
        with open(filename, 'rb') as file:
            pdf_reader = PyPDF2.PdfFileReader(file)
            num_pages = pdf_reader.numPages
            return num_pages
    except PyPDF2.utils.PdfReadError as e:
        messagebox.showerror("Error", "Selected file is not a PDF file.")
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None

def calculate_cost():
    global FilePath
    if not FilePath:
        messagebox.showinfo("Info", "Please select a file first.")
        return

    # Get the selected option
    option = var_option.get()
    value = prices[option]

    # Count pages
    num_pages = count_pages(FilePath)
    if num_pages is not None:
        total_price = num_pages * value
        lbl_price.config(text="Total Price: ₱ {:.2f}".format(total_price))
        lbl_pages.config(text="Total Pages: {}".format(num_pages))

def open_print_window():
    if not FilePath:
        messagebox.showinfo("Info", "No file selected")
    else:
        try:
            # Open the print window
            print_window = tk.Toplevel(root)
            print_window.title("Print Window")

            # Center the print window
            window_width = 300
            window_height = 300
            bg_color = "SkyBlue"
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width / 2) - (window_width / 2)
            y = (screen_height / 2) - (window_height / 2)
            print_window.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

            # Create labels
            lbl_file_name = tk.Label(print_window, text="File Name: " + FileName)
            lbl_file_name.pack(pady=10)

            num_pages = count_pages(FilePath)
            if num_pages is not None:
                lbl_page_count = tk.Label(print_window, text="Page Count: " + str(num_pages))
                lbl_page_count.pack(pady=10)

                lbl_color_option = tk.Label(print_window, text="Color Option: " + var_option.get())
                lbl_color_option.pack(pady=10)

                # Calculate total price
                option = var_option.get()
                value = prices[option]
                total_price = num_pages * value

                # Create label to display total price
                lbl_total_price = tk.Label(print_window, text="Total Price: ₱ {:.2f}".format(total_price))
                lbl_total_price.pack(pady=10)

                # Create button to print file
                btn_print_file = tk.Button(print_window, text="Print File", command=print_selected_file)
                btn_print_file.pack(pady=10)

                # Create button to close print window
                btn_close = tk.Button(print_window, text="Close", command=print_window.destroy)
                btn_close.pack(pady=10)

            else:
                # If count_pages() returned None, show an error message
                messagebox.showerror("Error", "Failed to count pages.")

        except Exception as e:
            messagebox.showerror("Error", str(e))



def print_selected_file():
    try:
        if not FilePath:
            raise ValueError("No file selected")

        # Check if the file is a PDF
        if not FilePath.lower().endswith(".pdf"):
            raise ValueError("Selected file is not a PDF file")

        if os.path.exists(FilePath):  # Check if the file exists
            if os.name == 'nt':  # Check if running on Windows
                os.startfile(FilePath, "print")
            else:
                # For other platforms, you might use a different method to print
                print("Printing is not supported on this platform.")
        else:
            print("File not found:", FilePath)

    except ValueError as e:
        messagebox.showerror("Error", str(e))


# Create the main window
root = tk.Tk()
root.title("File Explorer")

def reset_program():
    global FilePath, FileName
    FilePath = ""
    FileName = ""
    var_option.set("colored")  # Reset the radio button to default
    lbl_filename.config(text="File Name: ")  # Clear the file name label
    lbl_pages.config(text="Total Pages: 0")  # Reset the total pages label
    lbl_price.config(text="Total Price: ₱ 0.00")  # Reset the total price label

def close_print_window():
    global print_window, FilePath, FileName
    if print_window:
        print_window.destroy()

def convert_to_grayscale(FilePath):
    # Open the PDF
    pdf_document = fitz.open(FilePath)

    # Create a new PDF writer
    new_pdf = fitz.open()

    for page_number in range(len(pdf_document)):
        # Get the page
        page = pdf_document.load_page(page_number)

        # Convert the page to grayscale
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), colorspace="gray")

        # Create a new page in the new PDF
        new_page = new_pdf.new_page(width=pix.width, height=pix.height)

        # Insert the grayscale image of the page into the new page
        new_page.insert_image(new_page.rect, pixmap=pix)

    # Save the new PDF
    new_pdf.save("grayscale_" + FilePath)

def print_selected_file():
    try:
        if not FilePath:
            raise ValueError("No file selected")

        # Check if the file is a PDF
        if not FilePath.lower().endswith(".pdf"):
            raise ValueError("Selected file is not a PDF file")
        if var_option.get() == "non-colored":
            convert_to_grayscale(FilePath)

        if os.path.exists(FilePath):  # Check if the file exists
            if os.name == 'nt':  # Check if running on Windows
                os.startfile(FilePath, "print")
            else:
                # For other platforms, you might use a different method to print
                print("Printing is not supported on this platform.")
        else:
            print("File not found:", FilePath)

    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Set window icon
root.iconbitmap('C:/Users/Hp/Desktop/PYTHON_PRINTER_PROJ/Logo.ico')

# Maximize the window
root.state('zoomed')

canvas = tk.Canvas(root, bg="SkyBlue", width=1920, height=1080)
canvas.pack()

lbl_title = tk.Label(canvas, text="Insert Flash Drive", font=("Helvetica", 50))
lbl_title.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

btn_open = tk.Button(canvas, text="Choose File to print",font=("Helvetica", 20),  command=open_file_explorer, width=17, height=1)
btn_open.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

var_option = tk.StringVar(value="colored")
lbl_option = tk.Label(canvas, text="Select Print Option:", font=(20))
lbl_option.place(relx=0.5, rely=0.28, anchor=tk.CENTER)
radio_colored = tk.Radiobutton(canvas, text="Colored",font=(10), width=8, height=1, variable=var_option, value="colored", command=calculate_cost)
radio_colored.place(relx=0.4, rely=0.32)
radio_non_colored = tk.Radiobutton(canvas, text="Non-Colored", font=(10), width=10, height=1, variable=var_option, value="non-colored",
                                   command=calculate_cost)
radio_non_colored.place(relx=0.49, rely=0.32)

lbl_filename = tk.Label(canvas, text="File Name: ", font=("Helvetica", 12))
lbl_filename.place(relx=0.5, rely=0.52, anchor=tk.CENTER)

lbl_pages = tk.Label(canvas, text="Total Pages: 0", font=("Helvetica", 12))
lbl_pages.place(relx=0.5, rely=0.56, anchor=tk.CENTER)

lbl_price = tk.Label(canvas, text="Total Price: ₱ 0.00", font=("Helvetica", 12))
lbl_price.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

btn_print = tk.Button(canvas, text="Print", font=(10), width=10, height=1, command=open_print_window)
btn_print.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

btn_preview = tk.Button(canvas, text="Preview", font=(10), width=10, height=1, command=open_preview_window)
btn_preview.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

root.mainloop()

