from datetime import datetime, timedelta

import pandas as pd

from data_scraper import convert_runtime

import tkinter as tk
from tkinter import ttk, messagebox
from film_list import FilmList
from user_handler import UserHandler


class FilmExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Film Explorer")
        self.root.geometry("300x200")

        self.film_list = FilmList()
        self.filtered_list = self.film_list.film_data.copy()

        self.user_handler = UserHandler()
        self.login_menu()

    def login_menu(self):
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(self.login_frame, text="Enter your username", font=('Arial', 12, 'bold')).pack(side=tk.TOP, padx=5,
                                                                                                 pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.login_frame, textvariable=self.username_var, width=30)
        self.username_entry.pack(side=tk.TOP, padx=5, pady=5)

        login_button = ttk.Button(self.login_frame, text="Login", command=self.login, width=20)
        login_button.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.CENTER)

        add_user_button = ttk.Button(self.login_frame, text="Login as new user",
                                     command=lambda: self.login(as_new_user=True),
                                     width=20)
        add_user_button.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.CENTER)

    def login(self, as_new_user=False):
        self.username = self.username_var.get()

        if as_new_user:
            try:
                self.user_handler.add_user(self.username)
                messagebox.showinfo("User added", f"New user {self.username} added")
            except ValueError as e:
                messagebox.showerror("Username error", f'Username is incorrect.\n{e}')
                return
        elif not self.user_handler.exists(self.username):
            messagebox.showerror("User does not exist",
                                 "User does not exist. Try another username or login as new user")
            return

        self.list_to_watch, self.list_watched = self.user_handler.get_user_lists(self.username)

        messagebox.showinfo("Login", "Login Successful")
        self.create_widgets()
        self.show_data()

    def create_widgets(self):
        self.login_frame.destroy()
        self.root.geometry("1500x800")

        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # all films frame
        # ------------------------------------------------------------------
        # ------------------------------------------------------------------
        # search
        # ------------------------------------------------------------------
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.TOP, padx=10, pady=5, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.search)

        search_genre_frame = tk.Frame(main_frame)
        search_genre_frame.pack(fill=tk.X)

        ttk.Label(search_genre_frame, text="Search by Genre:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.genre_var = tk.StringVar()
        self.genre_entry = tk.Entry(search_genre_frame, textvariable=self.genre_var)
        self.genre_entry.pack(side=tk.BOTTOM, padx=10, pady=5, fill=tk.X, expand=True)
        self.genre_entry.bind("<KeyRelease>", self.search)

        # ------------------------------------------------------------------
        # filters
        # ------------------------------------------------------------------
        # dates
        # ------------------------------------------------------------------

        date_frame = tk.Frame(main_frame)
        date_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(date_frame, text="From Date").pack(side=tk.LEFT)
        self.date_from = ttk.Entry(date_frame)
        self.date_from.pack(side=tk.LEFT, padx=(26, 20))
        self.date_from.bind("<Return>", self.filter)

        ttk.Label(date_frame, text="To Date").pack(side=tk.LEFT)
        self.date_to = ttk.Entry(date_frame)
        self.date_to.pack(side=tk.LEFT, padx=(26, 20))
        self.date_to.bind("<Return>", self.filter)

        # runtime
        # ------------------------------------------------------------------

        runtime_frame = tk.Frame(main_frame)
        runtime_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(runtime_frame, text="From Runtime").pack(side=tk.LEFT)
        self.runtime_from = ttk.Entry(runtime_frame)
        self.runtime_from.pack(side=tk.LEFT, padx=(5, 20))
        self.runtime_from.bind("<Return>", self.filter)

        ttk.Label(runtime_frame, text="To Runtime").pack(side=tk.LEFT)
        self.runtime_to = ttk.Entry(runtime_frame)
        self.runtime_to.pack(side=tk.LEFT, padx=(5, 20))
        self.runtime_to.bind("<Return>", self.filter)

        # rating
        # ------------------------------------------------------------------

        rating_frame = tk.Frame(main_frame)
        rating_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(rating_frame, text="From Rating").pack(side=tk.LEFT)
        self.rating_from = ttk.Entry(rating_frame)
        self.rating_from.pack(side=tk.LEFT, padx=(16, 20))
        self.rating_from.bind("<Return>", self.filter)

        ttk.Label(rating_frame, text="To Rating").pack(side=tk.LEFT)
        self.rating_to = ttk.Entry(rating_frame)
        self.rating_to.pack(side=tk.LEFT, padx=(16, 20))
        self.rating_to.bind("<Return>", self.filter)

        # type, language
        # ------------------------------------------------------------------
        filters_frame = ttk.Frame(main_frame)
        filters_frame.pack(fill='both', expand=False, padx=10, pady=10)

        ttk.Label(filters_frame, text="Film type").pack(side=tk.LEFT)

        film_type = tk.StringVar()
        self.films_types = ttk.Combobox(filters_frame, textvariable=film_type)

        self.films_types['values'] = self.film_list.film_data['Type'].unique().tolist()
        self.films_types.pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Label(filters_frame, text="Language").pack(side=tk.LEFT)

        language_type = tk.StringVar()
        self.language_types = ttk.Combobox(filters_frame, textvariable=language_type)

        self.language_types['values'] = sorted(self.film_list.film_data['Language'].unique().tolist())
        self.language_types.pack(side=tk.LEFT, padx=5, pady=5)

        # buttons
        # ------------------------------------------------------------------
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        self.apply_filters_button = ttk.Button(buttons_frame, text="Apply", command=self.filter)
        self.apply_filters_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = ttk.Button(buttons_frame, text="Reset filters", command=self.reset_filters)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        # ------------------------------------------------------------------
        # treeview
        # ------------------------------------------------------------------

        self.notebook = ttk.Notebook(main_frame)

        frame_all_films = ttk.Frame(self.notebook)
        frame_to_watch = ttk.Frame(self.notebook)
        frame_watched = ttk.Frame(self.notebook)

        self.notebook.add(frame_all_films, text="Films")
        self.notebook.add(frame_to_watch, text="To Watch")
        self.notebook.add(frame_watched, text="Watched")
        self.notebook.bind('<<NotebookTabChanged>>', self.show_data)

        self.notebook.pack(expand=True, fill=tk.BOTH)

        self.prev_sorted_column = 'Release date'
        self.is_ascending_sorting = True

        head_columns = ('Original Index', 'Release date', 'Title', 'Genre', 'Runtime', 'Language', 'Type', 'Rating')

        self.tree_all = ttk.Treeview(frame_all_films, columns=head_columns, show='headings')
        self.tree_to_watch = ttk.Treeview(frame_to_watch, columns=head_columns, show='headings')
        self.tree_watched = ttk.Treeview(frame_watched, columns=head_columns, show='headings')

        self.create_film_tree(frame_all_films, tree=self.tree_all)
        self.create_film_tree(frame_to_watch, tree=self.tree_to_watch)
        self.create_film_tree(frame_watched, tree=self.tree_watched)

    def create_film_tree(self, tree_root, tree):

        tree.heading('Original Index', text='No.', command=lambda: self.sort_by_heading('Original Index', tree))
        tree.column('Original Index', width=25, anchor=tk.CENTER)

        tree.heading('Release date', text='Release date', command=lambda: self.sort_by_heading('Release date', tree))
        tree.column('Release date', width=60, anchor=tk.CENTER)

        tree.heading('Title', text='Title', command=lambda: self.sort_by_heading('Title', tree))
        tree.column('Title', width=300)

        tree.heading('Genre', text='Genre', command=lambda: self.sort_by_heading('Genre', tree))
        tree.column('Genre', width=120)

        tree.heading('Runtime', text='Runtime', command=lambda: self.sort_by_heading('Runtime', tree))
        tree.column('Runtime', width=40)

        tree.heading('Language', text='Language', command=lambda: self.sort_by_heading('Language', tree))
        tree.column('Language', width=80)

        tree.heading('Type', text='Type', command=lambda: self.sort_by_heading('Type', tree))
        tree.column('Type', width=80)

        tree.heading('Rating', text='Rating', command=lambda: self.sort_by_heading('Rating', tree))
        tree.column('Rating', width=25, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(expand=True, fill=tk.BOTH)

    def sort_by_heading(self, column, tree, event=None):
        for item in tree.get_children():
            tree.delete(item)

        if column == self.prev_sorted_column:
            self.is_ascending_sorting = not self.is_ascending_sorting
        else:
            self.is_ascending_sorting = True

        self.prev_sorted_column = column

        tree.heading(column)
        self.filtered_list = self.film_list.sort_by(column, ascending=self.is_ascending_sorting,
                                                    film_data=self.filtered_list)
        self.show_data()

    def search(self, event=None):
        query_title = self.search_var.get()
        query_genre = self.genre_var.get()

        list_to_show = self.filtered_list.copy()
        searched = False

        if query_title is not None or query_title != '':
            searched = True
            list_to_show = self.film_list.search_film(query_title, films=list_to_show)

        if query_genre is not None or query_genre != '':
            searched = True
            list_to_show = self.film_list.search_genre(query_genre, films=list_to_show)

        if searched:
            self.show_data(films=list_to_show)

    def filter(self, event=None):
        try:
            date_from = datetime.strptime(self.date_from.get(), '%Y-%m-%d')
        except ValueError:
            if self.date_from.get() != '':
                messagebox.showerror('Incorrect date format', 'Incorrect date format.'
                                                              'Format should be as follows:YYYY-MM-DD.\nExample: '
                                                              '2022-07-23')
            date_from = None

        try:
            date_to = datetime.strptime(self.date_to.get(), '%Y-%m-%d')
        except ValueError:
            if self.date_to.get() != '':
                messagebox.showerror('Incorrect date format', 'Incorrect date format.'
                                                              'Format should be as follows:YYYY-MM-DD.\nExample: '
                                                              '2022-07-23')
            date_to = None

        try:
            runtime_from = convert_runtime(self.runtime_from.get())
        except ValueError:
            if self.runtime_from.get() != '':
                messagebox.showerror('Incorrect runtime format',
                                     'Incorrect runtime format. Runtime format should be as '
                                     'follows: \'H h M min\' or \'HH:MM:SS\'')
            runtime_from = None

        try:
            runtime_to = convert_runtime(self.runtime_to.get())
        except ValueError:
            if self.runtime_to.get() != '':
                messagebox.showerror('Incorrect runtime format',
                                     'Incorrect runtime format. Runtime format should be as '
                                     'follows: \'H h M min\' or \'HH:MM:SS\'')
            runtime_to = None

        try:
            rating_from = float(self.rating_from.get())
        except ValueError:
            if self.rating_from.get() != '':
                messagebox.showerror('Incorrect rating format',
                                     'Incorrect rating format. Rating format should be float '
                                     'number')
            rating_from = 0.0

        try:
            rating_to = float(self.rating_to.get())
        except ValueError:
            if self.rating_to.get() != '':
                messagebox.showerror('Incorrect rating format',
                                     'Incorrect rating format. Rating format should be float '
                                     'number')
            rating_to = 10.0

        film_type = self.films_types.get()
        language = self.language_types.get()

        try:
            self.filtered_list = self.film_list.filter_by(date_from=date_from, date_to=date_to,
                                                          runtime_from=runtime_from, runtime_to=runtime_to,
                                                          rating_from=rating_from, rating_to=rating_to,
                                                          film_type=film_type, language=language)
        except ValueError as e:
            messagebox.showerror('Incorrect filters', f'Incorrect filters applied\n{e}')
            return

        self.search()

    def reset_filters(self, event=None):
        self.filtered_list = self.film_list.film_data.copy()
        self.date_from.delete(0, tk.END)
        self.date_to.delete(0, tk.END)
        self.runtime_from.delete(0, tk.END)
        self.runtime_to.delete(0, tk.END)
        self.rating_from.delete(0, tk.END)
        self.rating_to.delete(0, tk.END)
        self.films_types.set('')
        self.language_types.set('')
        self.search_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.prev_sorted_column = 'Release date'
        self.is_ascending_sorting = True

        self.show_data()

    def show_data(self, event=None, films=None):
        match self.notebook.index(self.notebook.select()):
            case 0:
                tree = self.tree_all
            case 1:
                tree = self.tree_to_watch
            case 2:
                tree = self.tree_watched

        for item in tree.get_children():
            self.tree_all.delete(item)

        if films is None:
            films = self.filtered_list.copy()

        films['Release date'] = films['Release date'].apply(lambda date: date.strftime('%B %d, %Y'))
        films['Runtime'] = films['Runtime'].apply(lambda td: f'{td.seconds // 3600} h {td.seconds // 60 % 60} min')

        for _, row in films.iterrows():
            tree.insert('', 'end', values=(row['Original Index'], row['Release date'],
                                           row['Title'], row['Genre'], row['Runtime'], row['Language'],
                                           row['Type'], row['Rating']))


if __name__ == "__main__":
    root = tk.Tk()
    app = FilmExplorerApp(root)
    root.mainloop()
