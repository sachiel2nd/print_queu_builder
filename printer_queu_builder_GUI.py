"""
Printer Queu Builder

"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pathlib
import re
import csv

	

class PrinterQueuBuilderGUI:
	def __init__(self, root):
		self.root = root
				
		
		
		self.rvws_data = {}
		self.inventory_numbers = {}
		self.merged_data = {}
		self.filtered_data = []
		self.blacklist = ["91782P01"]
		self.sales_keyword = "sales_01months"
		self.projection_keyword = "sales_01months"
		self.sale_keywords = {"01 months":"sales_01months", "03 months":"sales_03months", "06 months":"sales_06months", "12 months":"sales_12months", "18 months":"sales_18months"}
		self.sorting_column = "Quantity"
		self.sorting_asc = False
		
		self.table_columns = {
			"Code":"reference",
			"Quantity":"quantity",
			"Sales":"sales",
			"Projection":"projection",
			"Tdrive Stock":"stock_folder",
			"Backend Stock":"stock_backend",
			"CMYK":"cmyk",
			"White":"white",
			"Frost":"frost",
			"Gloss":"gloss"
			#active, id_product, id_category_default, id_product_attribute
			}
		self.build_gui()	

		
	def build_gui(self):
		
		self.root.title("Printer Queu Builder")
	   
		self.styles = ttk.Style()
		self.styles.configure("Button_green.TButton", background="green")
		self.styles.configure("Button_red.TButton", background="red")
		 
		notebook = ttk.Notebook(self.root)
		notebook.pack(fill='both', expand=True, padx=10, pady=10)
		
		
		search_tab = ttk.Frame(notebook)
		blacklist_tab = ttk.Frame(notebook)
		search_tab.columnconfigure(2, weight=1)
		search_tab.rowconfigure(8, weight=1)
		
		notebook.add(search_tab, text=" File Search ")
		notebook.add(blacklist_tab, text=" Blacklist Manager ")
		
		self.blacklist_widget = tk.Text(blacklist_tab, width=20, height=20, wrap="none")
		self.blacklist_widget.grid(row=1, column=1)
		
		self.rvw_directory = ttk.Button(search_tab, text = "RVW Directory", command= self.get_rvws)
		self.rvw_directory.grid(row=2, column=1, padx=2, pady=(4,4), sticky=tk.NW)
		
		self.inventory_file = ttk.Button(search_tab, text = "Invetory File", command= self.get_csv)
		self.inventory_file.grid(row=2, column=2, padx=2, pady=(4,4), sticky=tk.NW)
		
		
		##### UPPER OPTIONS #####
		upper_options_frame = tk.Frame(search_tab)
		upper_options_frame.grid(row=2, column=3, padx=2, pady=(4,4), columnspan = 7, sticky=tk.W)
		
		rvw_status_options = tk.LabelFrame(upper_options_frame, text= "RVW Filter(Placeholder)")
		rvw_status_options.grid(row=1, column=3, padx=1, pady=1, sticky=tk.E, rowspan = 4)
		self.rvw_filter = tk.IntVar(rvw_status_options, value=-1)
		tk.Radiobutton(rvw_status_options, text="NA", variable=self.rvw_filter, value=-1).grid(row=1, column=0, sticky=tk.W)
		tk.Radiobutton(rvw_status_options, text="Available", variable=self.rvw_filter, value=1).grid(row=2, column=0, sticky=tk.W)
		tk.Radiobutton(rvw_status_options, text="Unavailable", variable=self.rvw_filter, value=0).grid(row=3, column=0, sticky=tk.W)
		
		backend_status_options = tk.LabelFrame(upper_options_frame, text= "Backend Filter(Placeholder)")
		backend_status_options.grid(row=1, column=4, padx=1, pady=1, sticky=tk.E, rowspan = 4)
		self.backend_filter = tk.IntVar(backend_status_options, value=-1)
		tk.Radiobutton(backend_status_options, text="NA", variable=self.backend_filter, value=-1).grid(row=1, column=0, sticky=tk.W)
		tk.Radiobutton(backend_status_options, text="Available", variable=self.backend_filter, value=1).grid(row=2, column=0, sticky=tk.W)
		tk.Radiobutton(backend_status_options, text="Unavailable", variable=self.backend_filter, value=0).grid(row=3, column=0, sticky=tk.W)
		
		sales_selection_frame = tk.LabelFrame(upper_options_frame, text= "Sales timefram")
		sales_selection_frame.grid(row=1, column=1, padx=1, pady=1, rowspan = 2)
		self.sales_selection_widget = ttk.Combobox(sales_selection_frame,values=list(self.sale_keywords.keys()), state="readonly"  )
		self.sales_selection_widget.grid(row=1, column=1, padx=1, pady=1)
		
		projection_selection_frame = tk.LabelFrame(upper_options_frame, text= "Projection Timeframe")
		projection_selection_frame.grid(row=3, column=1, padx=1, pady=1, rowspan = 2)
		self.projection_selection_widget = ttk.Combobox(projection_selection_frame,values=list(self.sale_keywords.keys()), state="readonly" )
		self.projection_selection_widget.grid(row=1, column=1, padx=1, pady=1)
		
		
		##### LOWER OPTIONS #####
		
		self.search_widget = tk.Entry(search_tab)
		self.search_widget.grid(row=5, column=1, padx=4, pady=4, sticky="ew", columnspan = 2)
		self.search_widget.bind("<Return>", self.automatic_search)
		
		self.search_button = ttk.Button(search_tab, text = "Search", command= self.do_search)
		self.search_button.grid(row=6, column=1, padx=4, pady=4, sticky=tk.W)
		
		white_options = tk.LabelFrame(search_tab, text= "White filter")
		white_options.grid(row=4, column=4, padx=1, pady=1, rowspan = 4, sticky=tk.E)
		self.white_filter = tk.IntVar(white_options, value=-1)
		tk.Radiobutton(white_options, text="NA", variable=self.white_filter, value=-1).grid(row=1, column=0, sticky=tk.W)
		tk.Radiobutton(white_options, text="Yes", variable=self.white_filter, value=1).grid(row=2, column=0, sticky=tk.W)
		tk.Radiobutton(white_options, text="No", variable=self.white_filter, value=0).grid(row=3, column=0, sticky=tk.W)
		
		frost_options = tk.LabelFrame(search_tab, text= "Frost filter")
		frost_options.grid(row=4, column=5, padx=1, pady=1, rowspan = 4, sticky=tk.E)
		self.frost_filter = tk.IntVar(frost_options, value=-1)
		tk.Radiobutton(frost_options, text="NA", variable=self.frost_filter, value=-1).grid(row=1, column=0, sticky=tk.W)
		tk.Radiobutton(frost_options, text="Yes",variable=self.frost_filter, value=1).grid(row=2, column=0, sticky=tk.W)
		tk.Radiobutton(frost_options, text="No", variable=self.frost_filter, value=0).grid(row=3, column=0, sticky=tk.W)
		
		
		cmyk_options = tk.LabelFrame(search_tab, text= "CMYK filter")
		cmyk_options.grid(row=4, column=6, padx=1, pady=1, rowspan = 4, sticky=tk.E)
		self.cmyk_filter = tk.IntVar(cmyk_options, value=-1)
		tk.Radiobutton(cmyk_options, text="NA", variable=self.cmyk_filter, value=-1).grid(row=1, column=0, sticky=tk.W)
		tk.Radiobutton(cmyk_options, text="Yes", variable=self.cmyk_filter, value=1).grid(row=2, column=0, sticky=tk.W)
		tk.Radiobutton(cmyk_options, text="No", variable=self.cmyk_filter, value=0).grid(row=3, column=0, sticky=tk.W)
			
		backend_stock_frame = tk.LabelFrame(search_tab, text= "Backend stock")
		backend_stock_frame.grid(row=4, column=3, padx=1, pady=1, rowspan = 2)
		self.backend_stock_widget = ttk.Combobox(backend_stock_frame,values=["All"])
		self.backend_stock_widget.grid(row=1, column=1, padx=1, pady=1)
		
		tfolder_stock_frame = tk.LabelFrame(search_tab, text= "Tdrive stock")
		tfolder_stock_frame.grid(row=6, column=3, padx=1, pady=1, rowspan = 2)
		self.tfolder_stock_widget = ttk.Combobox(tfolder_stock_frame,values=["All"]  )
		self.tfolder_stock_widget.grid(row=5, column=1, padx=1, pady=1)
	   
		misc_options_frame = tk.LabelFrame(search_tab, text= "Misc")
		misc_options_frame.grid(row=4, column=7, padx=1, pady=1, rowspan = 4, sticky=tk.E)
		self.delete_blacklist_variable = tk.BooleanVar(value = False)
		delete_blacklist_q = tk.Checkbutton(misc_options_frame, variable = self.delete_blacklist_variable, text="Delete blacklisted codes")
		delete_blacklist_q.grid(row=0, column=0, padx=1, pady=1,sticky=tk.W)
		ignore_nofiles_q = tk.Checkbutton(misc_options_frame, text="placeholder")
		ignore_nofiles_q.grid(row=1, column=0, padx=1, pady=1,sticky=tk.W)
		self.normalize_quantities_variable = tk.BooleanVar()
		normalize_quantities_widget = tk.Checkbutton(misc_options_frame, variable = self.normalize_quantities_variable, text="Normalize quantities")
		normalize_quantities_widget.grid(row=2, column=0, padx=1, pady=1,sticky=tk.W)
		
		
		self.search_result_widget = ttk.Treeview(search_tab, columns=tuple(self.table_columns.keys()), show="headings")
		self.search_result_widget.grid(row=8, column=1,  padx=1, pady=5, columnspan = 7, sticky="ns")
		self.search_result_widget.bind("<Control-c>", self.copy_selection)
		
		for col in self.table_columns:
			self.search_result_widget.heading(column=col, text=col, command=lambda c=col: self.header_click(c))
		#self.search_result_widget.insert(self.search_result_widget, 1, ("mytext","mytext2","mytext3") )
		
	def dummy_function(self):
		return
		
	def get_rvws(self):
		folder_path = tk.filedialog.askdirectory(title="RVWs master folder")
		print(folder_path)
		pattern = r"([A-Z0-9]{8}) ?V?_?([CX][GX][FX][WX])\w*\.rvw"
		self.rvws_data = {}
		rvws_stocks = {}
		
		if folder_path == ():
			self.rvw_directory.configure(style = "Button_red.TButton")
			return
		try:
			formated_folder_path = pathlib.Path(folder_path)
			files = [(str(myfile.name), str(myfile.parent.name)) for myfile in formated_folder_path.rglob("??????*.rvw") if myfile.is_file()]	
			
			for myfile in files:
				reference = myfile[0][:8]
				if reference in list(self.rvws_data.keys()):
					self.rvws_data[reference]["duplicate"]= True
					print("duplicated!")
				else:
					match = re.search(pattern, myfile[0], re.IGNORECASE)
					if match:
						cmyk  = match.group(2)[0] == 'C'
						gloss = match.group(2)[1] == 'G'
						frost = match.group(2)[2] == 'F'
						white = match.group(2)[3] == 'W'
						self.rvws_data[reference] = {"reference":reference,"stock_folder":myfile[1], "duplicate":False, "cmyk":cmyk, "gloss":gloss,"frost":frost,"white":white}
						rvws_stocks[myfile[1]] = True
					
		except ArithmeticError:
			print("exception!")
		if self.rvws_data: 
			print(next(iter(self.rvws_data.values())))
			self.rvw_directory.configure(style = "Button_green.TButton")
		else:
			self.rvw_directory.configure(style = "Button_red.TButton")
		print(list(rvws_stocks.keys()))
		#self.tfolder_stock_widget.config(values=list(rvws_stocks.keys()).sort())
		self.tfolder_stock_widget["values"] = sorted(list(rvws_stocks.keys()))
		self.merge_dictionaries()
	
	def get_csv(self):
		folder_path = tk.filedialog.askopenfilename(title="cvs file", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
		print(folder_path)
		self.inventory_numbers = {}
		backend_stock = {}
		if not folder_path:
			self.inventory_file.configure(style = "Button_red.TButton")
			return

		with open(folder_path, mode='r', newline='',encoding='utf-8') as file:
				predata = csv.DictReader(file, delimiter=';')
				for myentry in predata:
					reference = myentry["reference"]
					self.inventory_numbers[reference] = myentry
					try: 
						quantity = int(myentry.get("quantity"))
					except:
						quantity = None
	
					if quantity == None:
						self.inventory_numbers[reference]["normalized_quantity"] = None
					elif quantity > 49000:
						self.inventory_numbers[reference]["normalized_quantity"] = quantity - 50000
					elif quantity > 9000:
						self.inventory_numbers[reference]["normalized_quantity"] = quantity - 10000
					elif quantity > 4000:
						self.inventory_numbers[reference]["normalized_quantity"] = quantity - 5000
					else:
						self.inventory_numbers[reference]["normalized_quantity"] = quantity
					backend_stock[myentry["stock_backend"]] = True
				if self.inventory_numbers: print(next(iter(self.inventory_numbers.values())))
#		except:
#			print("failed to open file")
		self.backend_stock_widget["values"] = sorted(list(backend_stock.keys()))
		if self.inventory_numbers: 
			self.inventory_file.configure(style = "Button_green.TButton")
		else:
			self.inventory_file.configure(style = "Button_red.TButton")
		self.merge_dictionaries()
			
	def merge_dictionaries(self):
		n=0
		m=0
		
		if self.rvws_data or self.inventory_file:
			print("value accepted")
			
			self.merged_data = self.rvws_data.copy()
			for key in self.inventory_numbers:
				
				if key in self.merged_data:
					self.merged_data[key] = self.merged_data[key]|self.inventory_numbers[key]
					n+=1
				else:
					self.merged_data[key] = self.inventory_numbers[key]
					m+=1
		else:
			print("no input")	
		if self.merged_data: print(list(self.merged_data.keys())[0],list(self.merged_data.values())[0],)
		print("n= ",n,"  m= ",m)
		print("rvw= ",len(self.rvws_data),"  inventory_file= ",len(self.inventory_numbers), "  merged= ",len(self.merged_data))
	
	def do_search(self):
		self.filter_data()
		self.update_table()
	
	def automatic_search(self, event):
		self.filter_data()
		self.update_table()
	
	def header_click(self, column_name):
		if column_name in self.table_columns.keys():
			
			if self.sorting_column == column_name:
				self.sorting_asc = not self.sorting_asc
			else:
				self.sorting_asc = False
			
			self.sorting_column = column_name
			
			self.filtered_data.sort(key=lambda x: self.sorting_function(x,self.table_columns[column_name]),reverse=self.sorting_asc  )
			self.update_table()
			print("header clicked! ", column_name," | ",self.table_columns[column_name] )
		
	
	def filter_data(self):
		white_filter = self.white_filter.get()
		cmyk_filter = self.cmyk_filter.get()
		frost_filter = self.frost_filter.get()
		
		backend_stock = self.backend_stock_widget.get()
		tfolder_stock = self.tfolder_stock_widget.get()
		
		search_string = self.search_widget.get()
		
		blacklist_filter = self.delete_blacklist_variable.get()
		self.blacklist = [str(line[:8]).lower() for line in self.blacklist_widget.get("1.0","end-1c").splitlines() if len(line) >= 8]
		
		if self.normalize_quantities_variable.get():
			self.table_columns["Quantity"] = "normalized_quantity"
			"Quantity"
		else:
			self.table_columns["Quantity"] =  "quantity"
		
		print(white_filter," | ",cmyk_filter," | ",frost_filter," | ",backend_stock," | ",tfolder_stock," | ",search_string)
		self.filtered_data = list(self.merged_data.values())
		
		if white_filter != -1:
			print("we entered white filter")
			self.filtered_data = [data_row for data_row in self.filtered_data if data_row.get("white") == white_filter]
		
		if cmyk_filter != -1:
			print("we entered cmyk filter")
			self.filtered_data = [data_row for data_row in self.filtered_data if data_row.get("cmyk") == cmyk_filter]
		
		if frost_filter != -1:
			print("we entered frost filter")
			self.filtered_data = [data_row for data_row in self.filtered_data if data_row.get("frost") == frost_filter]
		if backend_stock != "":
			print("we entered backend filter")
			self.filtered_data = [data_row for data_row in self.filtered_data if data_row.get("stock_backend") == backend_stock]
		if tfolder_stock != "":
			print("we entered tdrive filter")
			self.filtered_data = [data_row for data_row in self.filtered_data if data_row.get("stock_folder") == tfolder_stock]
		if search_string != "":
			print("we search pattern filter")
			self.filtered_data = [data_row for data_row in self.filtered_data if search_string.lower() in data_row.get("reference").lower() ]
		if blacklist_filter:
			print("we entered blacklist filter")
			self.filtered_data = [data_row for data_row in self.filtered_data if data_row.get("reference").lower() not in self.blacklist ]
		
		
		self.sorting_asc = False
		self.sorting_column = "Quantity"
		self.filtered_data.sort(key=lambda x: self.sorting_function(x,self.table_columns["Quantity"])  )

		return
		
				
	def update_table(self):
		self.search_result_widget.delete(*self.search_result_widget.get_children())	
		counter = 0 
		self.search_result_widget.tag_configure("normal_even", background="#F0F0F0")
		self.search_result_widget.tag_configure("normal_odd", background="#E0E0E0")
		self.search_result_widget.tag_configure("blacklisted", background="#777777")
		self.search_result_widget.tag_configure("duplicated", background="#FF7F7F")
		
		for data_row in self.filtered_data:
			code = data_row.get("reference")
			tdrive_stock = data_row.get("stock_folder")
			backend_stock= data_row.get("stock_backend")
			cmyk = data_row.get("cmyk")
			white = data_row.get("white")
			frost = data_row.get("frost")
			gloss = data_row.get("gloss")
			quantity = data_row.get(self.table_columns["Quantity"])
			sales = data_row.get("sales")
			projection = data_row.get("projection")
			
			if code.lower() in self.blacklist:
				mytag = "blacklisted"
				print("blacklisted tag found")
			elif data_row.get("duplicate"):
				print("duplicated tag found")
				mytag = "duplicated"
			elif counter % 2:
				mytag = "normal_even"
			else:
				mytag = "normal_odd"
			
			values_tuples = tuple(( "" if y is None else y) for y in  [code,quantity,sales, projection, tdrive_stock,backend_stock,cmyk,white,frost,gloss])
			self.search_result_widget.insert("", "end", values=values_tuples, tags=mytag)
			
			counter +=1
			if counter >= 99: break
		return
		
	def copy_selection(self, event):

		tree = self.search_result_widget
		
		selected_items = tree.selection()
		if not selected_items:
			return	
		codes = []
		for item in selected_items:
			values = tree.item(item, "values")
			if values:
				codes.append(str(values[0]))
		copy_text = "\n".join(codes)
		tree.clipboard_clear()
		tree.clipboard_append(copy_text)
		
	def sorting_function(self, mydic, keyword):
		row_value= mydic.get(keyword)
		try:
			numeric_value = int(row_value)
		except:
			numeric_value =	100000
		result = (
            (row_value is None),
            (numeric_value),
            (row_value)
        )
		return result		

	

def main():
	root = tk.Tk()
	app = PrinterQueuBuilderGUI(root)
	root.mainloop()


if __name__ == "__main__":
	main()
