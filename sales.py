import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Button, Label, Frame, Entry, messagebox, OptionMenu, StringVar

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sales"
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def read_data(query):
    conn = connect_db()
    if conn is None:
        print("Failed to connect to database")
        return pd.DataFrame()

    try:
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"Error reading data: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    
    return df

def plot_revenue_by_category():
    query = "SELECT product_category, SUM(revenue) AS total_revenue FROM online_sales GROUP BY product_category"
    df = read_data(query)
    
    if not df.empty:
        plt.figure(figsize=(10, 6))
        plt.bar(df['product_category'], df['total_revenue'])
        plt.xlabel('Product Category')
        plt.ylabel('Total Revenue')
        plt.title('Revenue by Product Category')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def plot_sales_by_payment_method():
    query = "SELECT payment_method, SUM(units_sold) AS total_units FROM online_sales GROUP BY payment_method"
    df = read_data(query)
    
    if not df.empty:
        plt.figure(figsize=(10, 6))
        plt.pie(df['total_units'], labels=df['payment_method'], autopct='%1.1f%%', startangle=140)
        plt.title('Sales Distribution by Payment Method')
        plt.axis('equal')
        plt.show()

def plot_monthly_sales_trend():
    query = """
    SELECT DATE_FORMAT(date, '%Y-%m') AS month, SUM(revenue) AS total_revenue
    FROM online_sales
    GROUP BY month
    ORDER BY month
    """
    df = read_data(query)
    
    if not df.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(df['month'], df['total_revenue'], marker='o')
        plt.xlabel('Month')
        plt.ylabel('Total Revenue')
        plt.title('Monthly Sales Trend')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def execute_query(query, params=()):
    conn = connect_db()
    if conn is None:
        print("Failed to connect to database")
        return

    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        messagebox.showinfo("Success", "Operation completed successfully")
    except mysql.connector.Error as e:
        print(f"Error executing query: {e}")
        messagebox.showerror("Error", f"Error executing query: {e}")
    finally:
        conn.close()

def create_data():
    query = """
    INSERT INTO online_sales (date, product_category, product_name, units_sold, unit_price, revenue, region, payment_method)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (entry_date.get(), category_var.get(), entry_name.get(), entry_units.get(), 
              entry_price.get(), entry_revenue.get(), entry_region.get(), payment_method_var.get())
    execute_query(query, params)

def read_data_from_table():
    query = 'SELECT * FROM online_sales'
    df = read_data(query)
    
    if not df.empty:
        show_data_popup(df)
    else:
        messagebox.showinfo("No Data", "No data found in the table")

def update_data():
    query = """
    UPDATE online_sales
    SET date = %s, product_category = %s, product_name = %s, units_sold = %s, unit_price = %s, revenue = %s, region = %s, payment_method = %s
    WHERE order_id = %s
    """
    params = (entry_date.get(), category_var.get(), entry_name.get(), entry_units.get(), 
              entry_price.get(), entry_revenue.get(), entry_region.get(), payment_method_var.get(), entry_order_id.get())
    execute_query(query, params)

def delete_data():
    query = 'DELETE FROM online_sales WHERE order_id = %s'
    params = (entry_order_id.get(),)
    execute_query(query, params)

def show_data_popup(df):
    top = tk.Toplevel()
    top.title("Data from Database")

    # Create a text widget to display the data
    text = tk.Text(top, wrap='none', height=20, width=100)
    text.pack(expand=True, fill='both')

    # Convert DataFrame to string and insert into text widget
    text.insert(tk.END, df.to_string(index=False))

    # Add a scrollbar to the text widget
    scrollbar = tk.Scrollbar(top, command=text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.config(yscrollcommand=scrollbar.set)

def show_main_menu():
    main_menu = tk.Toplevel()
    main_menu.title("Main Menu")

    frame = Frame(main_menu)
    frame.pack(padx=10, pady=10)

    Label(frame, text="Sales Data Visualization and Management", font=("Helvetica", 16)).pack(pady=10)

    Button(frame, text="Revenue by Product Category", command=plot_revenue_by_category).pack(pady=5)
    Button(frame, text="Sales Distribution by Payment Method", command=plot_sales_by_payment_method).pack(pady=5)
    Button(frame, text="Monthly Sales Trend", command=plot_monthly_sales_trend).pack(pady=5)

    Button(frame, text="Open CRUD Form", command=open_crud_form).pack(pady=5)

def open_crud_form():
    crud_form = tk.Toplevel()
    crud_form.title("CRUD Operations")

    frame = Frame(crud_form)
    frame.pack(padx=10, pady=10)

    Label(frame, text="Order ID").pack(pady=5)
    global entry_order_id
    entry_order_id = Entry(frame)
    entry_order_id.pack(pady=5)

    Label(frame, text="Date").pack(pady=5)
    global entry_date
    entry_date = Entry(frame)
    entry_date.pack(pady=5)

    Label(frame, text="Product Category").pack(pady=5)
    global category_var
    category_var = StringVar(value="Beauty Products")
    category_menu = OptionMenu(frame, category_var, "Beauty Products", "Clothing", "Books", "Sports", "Electronics", "Home Appliances")
    category_menu.pack(pady=5)

    Label(frame, text="Product Name").pack(pady=5)
    global entry_name
    entry_name = Entry(frame)
    entry_name.pack(pady=5)

    Label(frame, text="Units Sold").pack(pady=5)
    global entry_units
    entry_units = Entry(frame)
    entry_units.pack(pady=5)

    Label(frame, text="Unit Price").pack(pady=5)
    global entry_price
    entry_price = Entry(frame)
    entry_price.pack(pady=5)

    Label(frame, text="Revenue").pack(pady=5)
    global entry_revenue
    entry_revenue = Entry(frame)
    entry_revenue.pack(pady=5)

    Label(frame, text="Region").pack(pady=5)
    global entry_region
    entry_region = Entry(frame)
    entry_region.pack(pady=5)

    Label(frame, text="Payment Method").pack(pady=5)
    global payment_method_var
    payment_method_var = StringVar(value="Credit Card")
    payment_method_menu = OptionMenu(frame, payment_method_var, "Credit Card", "PayPal", "Debit Card")
    payment_method_menu.pack(pady=5)

    # CRUD Operation Buttons
    Button(frame, text="Create Data", command=create_data).pack(pady=5)
    Button(frame, text="Read Data", command=read_data_from_table).pack(pady=5)
    Button(frame, text="Update Data", command=update_data).pack(pady=5)
    Button(frame, text="Delete Data", command=delete_data).pack(pady=5)

# Main Menu
root = tk.Tk()
root.title('Sales Data Management')

# Show main menu on start
show_main_menu()

root.mainloop()
