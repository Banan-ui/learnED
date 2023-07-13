import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from PIL import ImageTk, Image
from settings import Settings
from db_sqlite import Database
from random import randint
import copy

class LearnED:
	def __init__(self):
		# Import of basic parameters
		self.settings = Settings()
		self.font = self.settings.font
		self.bold_font = self.settings.bold_font
		self.GREY = "#ccc"

		# Create a main window
		self.root = tk.Tk()
		self.root.title("learnED")
		win_geometry = f"{self.settings.screen_width}x{self.settings.screen_height}"
		self.root.geometry(win_geometry)
		self.root.resizable(True, True)

		# Import database
		self.database = Database()
		self.create_menu()

		# Import images
		self.img_import()

		self.create_main_frame()


#***************************************MAIN WINDOW

	def create_main_frame(self):
		# Drawing a main window
		# frame
		self.root_frame = self.create_scroll_bar(self.root)
		self.root_widgets_frame = tk.Frame(self.root_frame)
		self.root_widgets_frame.pack()

		# info
		self.create_main_info_tab(self.root_widgets_frame, 0)

		# buttons
		self.create_play_buttons_tab(self.root_widgets_frame, 8)


	def update_main_frame(self):
		# Update a main window
		self.clean_area(self.root)
		self.root_frame = self.create_scroll_bar(self.root)
		self.root_widgets_frame = tk.Frame(self.root_frame)

		self.root_widgets_frame.pack()

		self.create_main_info_tab(self.root_widgets_frame, 0)
		self.create_play_buttons_tab(self.root_widgets_frame, 8)


	def create_main_info_tab(self, frame, first_column):
		# Create a table with information about decks and cards
		# data
		all_tabs = self.database.get_all_tab_names()
		all_cards_counts = self.count_cards_from_all_tabs(
			function = self.database.get_cards_count_from_table)
		studied_cards_counts = self.count_cards_from_all_tabs(
			function = self.database.get_studied_cards_count)
		repeatable_cards_count = self.count_cards_from_all_tabs(
			function = self.database.get_repeatable_cards_count)

		# inserts
		if len(all_tabs) > 0:
			for l in [all_tabs, all_cards_counts, studied_cards_counts,
			 	repeatable_cards_count]:
				l.insert(0, "")

		all_tabs.insert(0, "Decks")
		all_cards_counts.insert(0, "All")
		studied_cards_counts.insert(0, "Learn")
		repeatable_cards_count.insert(0, "Repeat")

		# widgets
		for i in range(len(all_tabs)):
			widgets = [tk.Label(frame, text= all_tabs[i], width=21, anchor= tk.W)]
			for text in ["|", all_cards_counts[i], "|", studied_cards_counts[i],
			"|", repeatable_cards_count[i], "|"]:
				widgets.append(tk.Label(frame, text=text))

			if (i % 2) == 0: # Grey line
				for widget in widgets:
					widget.config(bg= self.GREY)

			if i > 1: # Highlighting numbers with color
				widgets[4].config(fg= "green")
				widgets[6].config(fg= "blue")

			for widget_num in range(len(widgets)):
				widgets[widget_num].config(font=self.font)
				widgets[widget_num].grid(row=i, column=widget_num, sticky= "nsew")


	def create_play_buttons_tab(self, frame, first_column):
		# buttons table for main window
		frame.grid_columnconfigure(first_column, weight= 1)

		# data
		all_tabs = self.database.get_all_tab_names()

		if len(all_tabs) == 0:
			tk.Label(frame, text="", bg=self.GREY, font= self.font, width=7).grid(row=0, 
				column=first_column, sticky= "nsew", columnspan=2)
			return 0
		else:
			tk.Label(frame, text="", bg=self.GREY, font= self.font).grid(row=0, 
				column=first_column, sticky= "nsew", columnspan=2)

		for i in range(len(all_tabs)):
			study_button = tk.Button(frame, image = self.light_start_img, 
				borderwidth=0, width=30,
				command= lambda name=all_tabs[i]: self.studing(name))
			repeat_button = tk.Button(frame, image = self.light_arrow_img, 
				borderwidth=0, width=30,
				command= lambda name=all_tabs[i]: self.repeating(name))
			
			if (i % 2) == 0: #Серая подсветка
				study_button.config(bg= self.GREY, image = self.dark_start_img,
				 	activebackground=self.GREY)				
				repeat_button.config(bg= self.GREY, image = self.dark_arrow_img,
				 	activebackground=self.GREY)

			study_button.grid(row= i+2, column=first_column)
			repeat_button.grid(row= i+2, column=first_column+1)


	def count_cards_from_all_tabs(self, function):
		# Returns a list of number of cards by the givern funnction from all decks
		all_tabs = self.database.get_all_tab_names()
		if all_tabs == []:
			return []

		cards_counts = []
		for tab in all_tabs:
			cards_counts.append(function(tab))

		return cards_counts


#***************************************CARDS STUDY/REPETITION

	def studing(self, name):
		# Redraw main window for studying cards
		checking = self.check_counts_of_cards(name, self.database.get_studied_cards_count, "learn")
		if not checking: # Cheking studying cards existing
			return 0
		# window
		self.clean_area(self.root)
		self.switch_menu("disable")
		self.root.title(name)
		
		# data
		self.tab_name = name
		self.id_list = self.database.get_all_studied_cards_id(self.tab_name)
		self.choose_button_function = self.create_studing_choose_buttons
		self.card = [0]

		# widgets
		self.draw_stable_widgets()

		self.show_new_card()


	def repeating(self, name):
		# Redraw main window for repeatable cards
		checking = self.check_counts_of_cards(name, self.database.get_repeatable_cards_count, "repeat")
		if not checking: # Cheding repeatable cards existing
			return 0		
		# window
		self.clean_area(self.root)
		self.switch_menu("disable")
		self.root.title("learnED")
		self.root.title(name)

		# data
		self.tab_name = name
		self.id_list = self.database.get_all_repetable_cards_id(self.tab_name)
		self.choose_button_function = self.create_repeating_choose_buttons
		self.card = [0]

		# widgets
		self.draw_stable_widgets()

		self.show_new_card()


	def draw_stable_widgets(self):
		# Drawing unchangeable windgets in the main window
		# frames
		top_frame = tk.Frame(self.root, bg=self.GREY)
		top_frame.place(y=0, relwidth= 1, relheight=0.08)

		self.button_frame = tk.Frame(self.root, bg=self.GREY)
		self.button_frame.place(relwidth= 1, relheight=0.15, rely=0.85)

		# widgets
		tk.Button(top_frame, text="<- back to menu", borderwidth=0, bg=self.GREY, 
			activebackground=self.GREY, font = self.font,
			command=self.back_to_main_frame).pack(side="left", padx=10)

		linie = "_"*70
		tk.Label(self.root, text=linie, font=self.font).place(x=0, rely=0.35, 
			relx=0.5, anchor="center")

		self.remaining_count_label = tk.Label(top_frame, bg=self.GREY,
			text=f"left : {len(self.id_list)}", borderwidth=0,font=self.font)
		self.remaining_count_label.pack(side="right", padx=10)


	def show_new_card(self):
		# Draw a window with a new card from list
		# data
		card_id = self.create_new_random_card_id()
		self.card = self.database.get_values_from_id(self.tab_name, card_id)

		# labels
		self.question_label = tk.Label(self.root, text=self.card[1], font=self.bold_font)
		self.question_label.place(x=0, rely=0.20, relx=0.5, anchor="center")

		self.answer_label = tk.Label(self.root, text=self.card[2], font=self.bold_font)

		tk.Button(self.button_frame, text="Show answer",
			font= self.font, command= self.show_answer).pack(pady= 10, expand=1)


	def create_new_random_card_id(self):
		# Selecting a randow index form the card list
		card_id = self.id_list[randint(0, len(self.id_list)-1)]

		if len(self.id_list) > 1 and card_id == self.card[0]:
			# Recall if the index falls on the current card
			return self.create_new_random_card_id()

		else: return card_id
 

	def show_answer(self):
		# Show the answer from the hidden part of the card
		self.answer_label.place(rely=0.50, relx=0.5, anchor="center")

		self.clean_area(self.button_frame)
		self.choose_button_function()


	def create_repeating_choose_buttons(self):
		# Creating card evaluation buttons for repeatable cards
		frame = tk.Frame(self.button_frame)
		frame.pack(pady=10, expand=1)
		tk.Button(frame, text="Forgot", fg="red", font= self.font, activeforeground= "red",
			command= lambda: self.change_level(-2, "rep")).pack(side="left")
		tk.Button(frame, text="Again", font= self.font,
			command= lambda: self.change_level(0, "stable")).pack(side="left")
		tk.Button(frame, text="Good", fg="green", font= self.font, activeforeground= "green",
			command= lambda: self.change_level(0, "rep")).pack(side="left")


	def create_studing_choose_buttons(self):
		# Creating card evaluation buttons for studied cards
		frame = tk.Frame(self.button_frame)
		frame.pack(pady=10, expand=1)
		tk.Button(frame, text="Hard", fg="red", font= self.font, activeforeground= "red", 
			command= lambda: self.change_level(-1, "std")).pack(side="left")
		tk.Button(frame, text="Normal", fg="blue", font= self.font, activeforeground= "blue",
			command= lambda: self.change_level(0,"std")).pack(side="left")
		tk.Button(frame, text="Easy", fg="green", font= self.font, activeforeground= "green",
			command= lambda: self.change_level(1, "std")).pack(side="left")


	def change_level(self, value, type):
		# Change a level of card
		level = self.card[3] + value
		if level < 0: level = 0

		self.database.set_new_level(self.tab_name, self.card[0], level)

		if type == "std" or type == "rep": # The card relates to what is being studied or repeated
			if level == 3: # The card is considered learned
				self.id_list.remove(self.card[0])
				self.remaining_count_label.config(text= f"left : {len(self.id_list)}")
		if type == "rep": # The card refers to a repeatable
			if level < 3: # The card is considered forgotten
				self.id_list.remove(self.card[0])
				self.remaining_count_label.config(text= f"left : {len(self.id_list)}")
		if type == "stable": # Repetition of the card without changes
			None

		if len(self.id_list) == 0: # No more cards in list
			self.back_to_main_frame()
		else:
			self.reload_area_for_new_card()


	def reload_area_for_new_card(self):
		# Updating the window to draw a new card
		self.clean_area(self.button_frame)
		self.question_label.destroy()
		self.answer_label.destroy()

		self.show_new_card()


	def back_to_main_frame(self):
		# Return to the main window table
		self.clean_area(self.root)
		self.switch_menu("normal")
		self.create_main_frame()
		self.root.title("LeanED")



	def check_counts_of_cards(self, name, function, message):
		# Checks the availability of cards for the specified function
		if function(name) > 0:
			return True
		else:
			tk.messagebox.showerror(title="No cards found",
				message= f"You have no cards for {message}")
			return 0


	def clean_area(self, area):
		# Removing all widgets from the specified plane except the main menu
		for widget in area.winfo_children():
			if not isinstance(widget, tk.Menu):
				widget.destroy()


	def switch_menu(self, command):
		# On/Off menu
		for menu in [self.table_menu, self.card_menu, self.info_menu]:
			last = menu.index("end")
			for i in range(last+1):
				menu.entryconfigure(i, state= command)


#***************************************MAIN MENU

	def create_menu(self):
		# Create main menu
		self.main_menu = tk.Menu(self.root)
		self.root.config(menu = self.main_menu)

		# Submenu of decks
		self.table_menu = tk.Menu(self.main_menu, tearoff= 0)
		self.table_menu.add_command(label = "Create a deck", 
									command= self.create_tab_window)
		self.del_tab_submenu = tk.Menu(self.table_menu, tearoff= 0)
		self.table_menu.add_cascade(label = "Delete a deck",
									menu= self.del_tab_submenu)
		self.create_tab_submenu(self.del_tab_submenu, self.delete_tab)

		self.check_tab_submenu= tk.Menu(self.table_menu, tearoff= 0)
		self.table_menu.add_cascade(label = "View the cards in the deck",
									menu = self.check_tab_submenu)
		self.create_tab_submenu(self.check_tab_submenu, self.create_check_tab_window)


		self.main_menu.add_cascade(label= "Decks", menu= self.table_menu)

		# Submenu of cards
		self.card_menu = tk.Menu(self.main_menu, tearoff= 0)
		self.card_menu.add_command(label = "Add a card",
									command = self.check_table_existence)
		self.tab_del_card_submenu = tk.Menu(self.card_menu, tearoff= 0)
		self.card_menu.add_cascade(label = "Delete and edit cards",
									menu= self.tab_del_card_submenu)
		self.create_tab_submenu(self.tab_del_card_submenu, self.delete_card_window)

		self.main_menu.add_cascade(label= "Cards", menu= self.card_menu)

		# Submenu for info
		self.info_menu = tk.Menu(self.main_menu, tearoff= 0)
		self.main_menu.add_cascade(label= "Info", menu= self.info_menu)
		self.info_menu.add_command(label="Statistics",
			command = self.create_info_window)


	def create_tab_submenu (self, menu_bar, function):
		# Create submenu from tables names
		tab_names = self.database.get_all_tab_names()
		for name in tab_names:
			menu_bar.add_command(label = name, command= lambda name=name: function(name))


	def recreate_all_submenus(self):
		# Redrawing all submenus from table names
		self.recreate_submenu(self.del_tab_submenu, self.delete_tab)
		self.recreate_submenu(self.tab_del_card_submenu, self.delete_card_window)
		self.recreate_submenu(self.check_tab_submenu, self.create_check_tab_window)


	def recreate_submenu(self, submenu, command):
		# Delete and create submenu
		last_index = submenu.index('end')
		if last_index != None:
			for i in range(last_index+1):
				submenu.delete(0)
		self.create_tab_submenu(submenu, command)


#**************************************DECK MANAGEMENT

	def create_tab_window(self):
		# Create a second window for creating a new table
		self.tab_window = tk.Toplevel(self.root)
		self.tab_window.grab_set()
		self.tab_window.resizable(False, False)
		self.tab_window.geometry("300x100")
		self.tab_window.title("New deck")

		self.create_tab_label = tk.Label(self.tab_window, 
			text="Enter the name of the new deck", font=self.font, anchor="center")
		self.create_tab_label.pack(pady=5, padx=5)

		entry = tk.Entry(self.tab_window, width=30, font=self.font)
		entry.pack()

		button = tk.Button(self.tab_window, text="Create", 
			command= lambda: self.check_new_name_tab(entry.get()), width=15).pack(pady=7)


	def check_new_name_tab(self, name):
		# Check the entered name ro create a new table
		tab_names = self.database.get_all_tab_names()
		if name == "":
			self.create_tab_label.config(text = "The entry must not to be empty", fg= "red")
		elif name in tab_names:
			self.create_tab_label.config(text = "This deck already exists", fg= "red")
		else: self.create_tab(name)


	def create_tab(self, name):
		# Create a new table
		self.database.create_new_tab(name)
		self.create_tab_label.config(text = "Added!", fg= "green")
		self.tab_window.after(1000, lambda:self.tab_window.destroy())
		self.tab_window.after(100, lambda:self.update_main_frame())

		self.recreate_all_submenus()


	def delete_tab(self, name):
		# delete table
		# messagebox for deleting table
		answer = messagebox.askquestion(title= "Delete",
			message=f"Are you sure you want to delete the '{name}' deck?")
		if answer == "yes":
			self.database.delete_tab(name)
			self.recreate_all_submenus()
			self.update_main_frame()


#**************************************CARD MANAGMENT

	def check_cards_in_table_existence(self, name):
		# Check existing cards in the deck
		if self.database.get_cards_count_from_table(name) > 0:
			return True
		else:
			tk.messagebox.showerror(title="No cards found",
				message= f"You haven't added any cards to your deck")
			return 0


	def check_table_existence(self):
		# Check existing tables in database
		if self.database.get_all_tab_names() == []:
			tk.messagebox.showerror(title="No decks found", 
				message= "You have not created any decks")
		else: self.create_card_window()


#******************Add card window

	def create_card_window(self):
		# Create a second window for creating new cards
		self.add_card_window = tk.Toplevel(self.root)
		self.add_card_window.grab_set()
		self.add_card_window.resizable(False, False)
		self.add_card_window.geometry("300x200")
		self.add_card_window.title("Adding cards")

		tab_frame = tk.Frame(master = self.add_card_window)
		input_frame = tk.Frame(master = self.add_card_window)
		tab_frame.pack(padx= 5, pady= 10)
		input_frame.pack(padx= 5)

		# tab_frame
		label = tk.Label(master = tab_frame, text = "Deck:", font=self.font)
		label.pack(side = "left", pady= 3)
		values = self.database.get_all_tab_names()
		combobox = ttk.Combobox(master = tab_frame, value=values)
		combobox.set(values[len(values)-1])
		combobox.pack(padx = 5, pady= 3)

		# input_frame
		self.first_label = tk.Label(master = input_frame, anchor = "center",
			text= "Front side of the card", font=self.font)
		self.first_entry = tk.Entry(master=input_frame, width=30, font=self.font)
		self.first_label.pack(pady=3)
		self.first_entry.pack()

		self.second_label = tk.Label(master = input_frame, anchor = "center",
			text= "Back side of the card", font=self.font)
		self.second_entry = tk.Entry(master=input_frame, width=30, font=self.font)
		self.second_label.pack(pady=3)
		self.second_entry.pack()

		button = tk.Button(master= input_frame, text="Add", width=15,
			command= lambda: self.check_new_info_card(combobox.get(),
			self.first_entry.get(), self.second_entry.get())).pack(pady=10)


	def check_new_info_card(self, table, front_text, back_text):
		# Cheking entry in the window of card creation
		temmporary_bool= True
		if table not in self.database.get_all_tab_names():temmporary_bool = False
		if front_text == "":
			self.first_label.config(text = "The entry must not to be empty", fg= "red")
			temmporary_bool = False
		if back_text == "":
			self.second_label.config(text = "The entry must not to be empty", fg= "red")
			temmporary_bool = False
		if temmporary_bool: # Create new card
			self.reset_card_window_settings()
			self.database.create_new_card(table, front_text, back_text)

			# Redraw main window
			self.add_card_window.after(50, 
				lambda:self.create_main_info_tab(self.root_widgets_frame, 0))


	def reset_card_window_settings(self):
		# Clear entrys in card creation window
		self.first_entry.delete(0, tk.END)
		self.second_entry.delete(0, tk.END)
		self.first_label.config(text = "Front side of the card", fg= "black")
		self.second_label.config(text = "Back side of the card", fg= "black")


#******************Window for deleting and editing cards

	def delete_card_window(self, name):
		# Create a window for editing and deleting cards
		cards_existence = self.check_cards_in_table_existence(name)
		if not cards_existence:
			return 0

		# window
		self.del_card_window = tk.Toplevel(self.root)
		self.del_card_window.grab_set()
		self.del_card_window.geometry("700x400")
		self.del_card_window.title(f"{name}")

		# frame
		self.del_card_frame = self.create_scroll_bar(self.del_card_window)

		# info tab
		self.create_info_tab(self.del_card_frame, name)

		# buttons tab
		self.create_buttons_tab(self.del_card_frame, name, 3)


	def create_buttons_tab(self, frame, name, first_column):
		# Create a table for deleting and editing cards

		id_list = self.database.get_cards_list(name, "id")

		tk.Label(frame, text="|", bg=self.GREY, font=self.font).grid(row=0, column=first_column)
		tk.Label(frame, text="|", font=self.font).grid(row=1, column=first_column)
		tk.Label(frame, text="", bg=self.GREY).grid(row=0, column=first_column+1,
			sticky= "nsew", columnspan=2)

		for i in range(0, len(id_list)):
			del_button = tk.Button(frame, image = self.light_bin_img, 
				borderwidth=0, width=35,
				command= lambda card_id=id_list[i]: self.delete_card(card_id, name))
			edit_button = tk.Button(frame, image = self.light_pencil_img,
				borderwidth=0, width=35, 
				command= lambda card_id=id_list[i]: self.create_edit_card_window(card_id, name))
			linie = tk.Label(frame, text="|")

			if (i % 2) == 0:
				linie.config(bg = self.GREY)
				del_button.config(bg= self.GREY, image = self.dark_bin_img,
				 	activebackground=self.GREY)
				edit_button.config(bg= self.GREY, image = self.dark_pencil_img,
				 	activebackground=self.GREY)

			linie.grid(row= i+2, column= first_column, sticky= "nsew")
			edit_button.grid(row= i+2, column=first_column+1)	
			del_button.grid(row= i+2, column=first_column+2)

							
	def create_info_tab(self, frame, name, first_column=0):
		# Create info tabel
		front_list = self.database.get_cards_list(name, "front")
		back_list = self.database.get_cards_list(name, "back")
		front_list.insert(0, "")
		front_list.insert(0, "Front text")
		back_list.insert(0, "")
		back_list.insert(0, "Back text")

		frame.grid_columnconfigure(first_column, weight= 1, uniform= "col")
		frame.grid_columnconfigure(first_column+2, weight= 1, uniform= "col")

		for i in range(0, len(front_list)):
			front_label = tk.Label(frame, text= front_list[i], width= 20, font=self.font)
			first_linie = tk.Label(frame, text="|", font=self.font)
			back_label = tk.Label(frame, text= back_list[i], width= 20, font=self.font)

			if (i % 2) == 0: # Grey lines
				for module in [front_label, first_linie, back_label]:
					module.config(bg= self.GREY)

			front_label.grid(row= i, column= first_column, sticky= "nsew")
			first_linie.grid(row= i, column= first_column+1, sticky= "nsew")
			back_label.grid(row= i, column= first_column+2, sticky= "nsew")


	def delete_card(self, card_id, name):
		# Delete card from database
		answer = messagebox.askquestion(title= "Delete",
			message=f"Delete this card?")
		if answer == "yes":
			self.database.delete_card(card_id, name)
			self.restart_del_card_window(self.del_card_frame, name)
			self.create_main_info_tab(self.root_widgets_frame, 0) # Redraw main window


	def restart_del_card_window(self, frame, name):
		# Deleting widgets in the card deletion window
		for widget in frame.winfo_children():
			widget.destroy()

		#Проверка налчия в таблице карточек
		if self.database.get_cards_count_from_table(name) == 0:
			self.del_card_window.destroy() # Close the window
		else:
			self.update_delete_card_window(name) # Redrow window


	def update_delete_card_window(self, name):
		# Redrawing the deleting and editing cards window
		self.create_info_tab(self.del_card_frame, name) # Redraw table
		self.create_buttons_tab(self.del_card_frame, name, 3) # Redraw buttons


#******************Card editing window

	def create_edit_card_window(self, card_id, name):
		# Create a window for editing card
		self.edit_card_window = tk.Toplevel(self.root)
		self.edit_card_window.grab_set()
		self.edit_card_window.geometry("300x150")
		self.edit_card_window.title(f"Edit")
		self.edit_card_window.resizable(False, False)

		values = self.database.get_values_from_id(name, card_id)

		self.first_label = tk.Label(self.edit_card_window, anchor = "center",
			text= "Front text", font=self.font)
		self.first_entry = tk.Entry(self.edit_card_window, width=30, font=self.font)
		self.first_label.pack(pady=5)
		self.first_entry.pack()

		self.second_label = tk.Label(self.edit_card_window, anchor = "center",
			text= "Back text", font=self.font)
		self.second_entry = tk.Entry(self.edit_card_window, width=30, font=self.font)
		self.second_label.pack(pady=5)
		self.second_entry.pack()

		self.first_entry.insert(0, values[1])
		self.second_entry.insert(0, values[2])

		button = tk.Button(self.edit_card_window, text="Edit", width=15,
			command= lambda: self.check_edit_info_card(name, card_id,
			self.first_entry.get(), self.second_entry.get())).pack(pady=10)


	def check_edit_info_card(self, name, card_id, front_text, back_text):
		# Check entry tin card editing window
		temmporary_bool= True
		if front_text == "":
			self.first_label.config(text = "The entry must not to be empty", fg= "red")
			temmporary_bool = False
		if back_text == "":
			self.second_label.config(text = "The entry must not to be empty", fg= "red")
			temmporary_bool = False
		if temmporary_bool:
			#Editing
			self.database.edit_card(name, card_id, front_text, back_text)
			self.update_delete_card_window(name)
			self.edit_card_window.destroy()


#******************Card view window

	def create_check_tab_window(self, name):
		# Create a window for viewing cards
		cards_existence = self.check_cards_in_table_existence(name)
		if not cards_existence:
			return 0

		self.check_tab_window = tk.Toplevel(self.root)
		self.check_tab_window.grab_set()
		self.check_tab_window.geometry("700x400")
		self.check_tab_window.title(f"{name}")

		# frame
		self.check_tab_frame = self.create_scroll_bar(self.check_tab_window)

		# tab
		self.create_nummer_tab(self.check_tab_frame, name, first_column=0)

		# info_tab
		self.create_info_tab(self.check_tab_frame, name, first_column=2)


	def create_nummer_tab(self, frame, name, first_column=0):
		# Create a table of sequentially numbered table
		count = self.database.get_cards_count_from_table(name)
		count_list = [i for i in range(1, count+1)]
		count_list.insert(0, "")
		count_list.insert(0, "№")

		for i in range(len(count_list)):
			nummer_label = tk.Label(frame, text=count_list[i], width=4, font=self.font)
			linie_frame = tk.Label(frame, text="|", font=self.font)

			if (i % 2) == 0:
				nummer_label.config(bg= self.GREY)
				linie_frame.config(bg= self.GREY)

			nummer_label.grid(row=i, column= first_column, sticky= "nsew")
			linie_frame.grid(row=i, column= first_column+1)


#**************************************INFO WINDOW

	def create_info_window(self):
		# Create info window
		info_window = tk.Toplevel(self.root)
		info_window.grab_set()
		info_window.title("Info")
		info_window.resizable(False, False)

		# data
		all_tabs = self.database.get_all_tab_names()
		learning_cards, repeating_cards = 0, 0
		for name in all_tabs:
			learning_cards += self.database.get_studied_cards_count(name)
			repeating_cards += self.database.get_repeatable_cards_count(name)
		cards_sum = learning_cards+repeating_cards

		# Labels
		l = ["Total decks:", len(all_tabs), "Total cards:", cards_sum, 
		"Learning cards:", learning_cards, "Repeating cards:", repeating_cards]
		widgets= []
		for text in l:
			widgets.append(tk.Label(info_window, text= text, font= self.font))
		widgets[5].config(fg="green")
		widgets[7].config(fg="blue")

		row = 0
		for i in range(0, len(widgets), 2):
			widgets[i].grid(row=row, column= 0, padx=5)
			row += 1

		row = 0
		for i in range(1, len(widgets), 2):
			widgets[i].grid(row=row, column= 1 ,padx=5)
			row += 1


#******************Scroll bar

	def create_scroll_bar(self, window, set_width=0, x=0):
		# Creating a scroll bar and frame for widgets
		first_frame = tk.Frame(window) # Main frame
		first_frame.pack(fill= tk.BOTH, expand = 1)

		canvas = tk.Canvas(first_frame, highlightbackground = self.GREY) 
		canvas.pack(side= tk.LEFT, fill= tk.BOTH, expand = 1)

		scrollbar = ttk.Scrollbar(first_frame, orient= tk.VERTICAL, command= canvas.yview)
		scrollbar.pack(side= tk.RIGHT, fill= tk.Y)

		second_frame = tk.Frame(canvas) # Frame for all windgets
		canvas.create_window((x, 0), window = second_frame, anchor= "nw")
		canvas.bind('<Configure>', lambda e:self.resize_win(e.width, e.height, 
			canvas, second_frame, scrollbar, set_width, x))
		canvas.configure(yscrollcommand= scrollbar.set)

		# Return the frame for widgets
		return second_frame 


	def resize_win(self, width, canvas_height, canvas, frame, scrollbar, set_width, x):
		# Redraw a 'window' inside of canvas block
		frame_height = frame.winfo_height()
		if set_width != 0:
			width = set_width
		if canvas_height < frame_height:
			height = frame_height
		else:
			height = canvas_height

		canvas.create_window((x, 0), window = frame, width= width,
		 	height= height, anchor= "nw")
		canvas.configure(scrollregion = canvas.bbox("all"))


#**************************************other

	def img_import(self):
		# Import images
		self.light_bin_img = ImageTk.PhotoImage(file = "images/light_bin.png")
		self.dark_bin_img = ImageTk.PhotoImage(file = "images/dark_bin.png")
		self.light_pencil_img = ImageTk.PhotoImage(file = "images/light_pencil.png")
		self.dark_pencil_img = ImageTk.PhotoImage(file = "images/dark_pencil.png")

		self.dark_arrow_img = ImageTk.PhotoImage(file = "images/dark_arrow.png")
		self.light_arrow_img = ImageTk.PhotoImage(file = "images/light_arrow.png")
		
		self.dark_start_img = ImageTk.PhotoImage(file = "images/dark_start.png")
		self.light_start_img = ImageTk.PhotoImage(file = "images/light_start.png")


	def app_start(self):
		# Run the app
		self.root.mainloop()


if __name__ == '__main__':
	# Create and run the application
	led = LearnED()
	led.app_start()