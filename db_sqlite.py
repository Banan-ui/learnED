import sqlite3

class Database():
	def __init__(self):

		self.db = sqlite3.connect('main_db.sqlite')
		self.cursor = self.db.cursor()


	def create_new_tab(self, name):
		# Create new table in database
		self.cursor.execute(f"""CREATE TABLE '{name}'
			(id INTEGER PRIMARY KEY,
			front TEXT NOT NULL,
			back TEXT NOT NULL,
			level INTEGER NOT NULL);""")

	def delete_tab(self, name):
		# Deleting table from database
		self.cursor.execute(f"DROP TABLE IF EXISTS '{name}'")
		self.db.commit()

	def get_all_tab_names(self):
		# Return a list of names of all tables in database
		name_list = []
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
		not_sort_name_list = self.cursor.fetchall()
		for name in not_sort_name_list:
			name_list.append(name[0])
		return name_list

	def get_cards_count_from_table(self, name):
		# return count of records in table
		self.cursor.execute(f"SELECT COUNT(*) FROM '{name}'")
		count = self.cursor.fetchone()[0]
		return count

	def get_studied_cards_count(self, name):
		# Counting the number of studying records in the table
		self.cursor.execute(f"SELECT COUNT(*) FROM '{name}' WHERE level < 3")
		count = self.cursor.fetchone()[0]
		return count

	def set_new_level(self, name, card_id, level):
		# Update level
		self.cursor.execute(f"""UPDATE '{name}' SET level = {level}
			WHERE id = '{card_id}'""")
		self.db.commit()

	def get_repeatable_cards_count(self, name):
		# Counting the number of repeating records in the table
		self.cursor.execute(f"SELECT COUNT(*) FROM '{name}' WHERE level = 3")
		count = self.cursor.fetchone()[0]
		return count

	def get_all_studied_cards_id(self, name):
		# Return a id list of studying records
		self.cursor.execute(f"SELECT id FROM '{name}' WHERE level < 3")
		l = self.sort_data(self.cursor.fetchall())
		return l

	def get_all_repetable_cards_id(self, name):
		# Return a id list of repeating records
		self.cursor.execute(f"SELECT id FROM '{name}' WHERE level = 3")
		l = self.sort_data(self.cursor.fetchall())
		return l

	def sort_data(self, l):
		for i in range(len(l)):
			l[i] = l[i][0]
		return l


	def get_cards_list(self, name, value):
		# Sequential list of all specified values in the table
		self.cursor.execute(f"SELECT {value} FROM '{name}'")
		count = self.cursor.fetchall()

		list_of_value = []
		for i in count:
			list_of_value.append(i[0])
		return list_of_value

	def get_values_from_id(self, name, card_id):
		# Geting all records from id's
		self.cursor.execute((f"SELECT * FROM '{name}' WHERE id = '{card_id}'"))
		values = self.cursor.fetchone()
		return values

	def edit_card(self, name, card_id, front_text, back_text):
		# Change record in table
		self.cursor.execute(f"""UPDATE '{name}' SET front = '{front_text}',
		 	back = '{back_text}' WHERE id = '{card_id}'""")
		self.db.commit()


	def delete_card(self, card_id, name):
		# Delete record from table
		self.cursor.execute(f"DELETE FROM '{name}' WHERE id = '{card_id}'")
		self.db.commit()


	def create_new_card(self, table, front, back):
		# Add record to a table
		self.cursor.execute(f"""INSERT INTO '{table}'
			(front, back, level) VALUES ('{front}', '{back}', 0)""")
		self.db.commit()




