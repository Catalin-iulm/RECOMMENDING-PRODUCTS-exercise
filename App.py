# Import necessary libraries
import pandas as pd
import streamlit as st
from io import StringIO
import matplotlib.pyplot as plt

# Load the uploaded file
# The file name is 'Groceries_dataset.csv'
file_name = 'Groceries_dataset.csv'
df = pd.read_csv(file_name, sep=';')

# --- Data Inspection (Simulated as we can't print within this block directly for Streamlit) ---
# In a normal script, you would do:
# print(df.head())
# print(df.info())
# print(df.columns) # From the preview, columns are ID;freq;F1;F2;...;concat;;
# The last column seems to be 'concat;;' which might be problematic, or it's an unnamed column after 'concat'.
# Let's assume the last column without a proper name is the one with concatenated items,
# or the items are spread across F1 to F164.
# From the preview, the 'concat;;' column (or the one before it if that's a typo) seems to be the one containing the items.
# Let's rename the problematic last column if it exists, or use the 'concat' column.
# Based on the preview, the last column seems to be the relevant one for items.
# The file has issues with the last column name and potentially double semicolons at the end of lines.

# Let's try to identify the item column.
# The preview shows items like "pastry,salty snack,whole milk" in the last column.
# Let's assume the items are in the column named 'concat;;' or it's the last column.
# Pandas might read 'concat;;' as 'concat' and then an unnamed column.
# Let's check the actual columns from df.columns
# If 'concat;;' is a column name:
item_column_name = None
if 'concat;;' in df.columns:
    item_column_name = 'concat;;'
elif 'concat' in df.columns: # In case pandas corrected it
    item_column_name = 'concat'
else:
    # Fallback: check the last few columns for a pattern of items
    # For now, let's assume the user has preprocessed this or it's the 'itemDescription' from a different dataset version
    # Given the file structure, it's more likely the items are in a column formed from 'F1' to 'F164' and then 'concat'
    # The items are in the last column, let's try to access it by index if name is tricky
    if df.shape[1] > 166 : # ID, freq, 164 F columns, concat, unnamed
        item_column_name = df.columns[166]


# --- Data Preprocessing ---
all_items = []
if item_column_name and item_column_name in df.columns:
    # Drop rows where the item description is NaN
    df_cleaned = df.dropna(subset=[item_column_name])
    for index, row in df_cleaned.iterrows():
        # Split the string by comma and strip whitespace from each item
        items_in_transaction = [item.strip() for item in str(row[item_column_name]).split(',') if item.strip()]
        all_items.extend(items_in_transaction)
else:
    # Alternative strategy: If items are in F1 to F164
    item_cols = [f'F{i}' for i in range(1, 165)]
    # Check which of these columns exist
    existing_item_cols = [col for col in item_cols if col in df.columns]
    if existing_item_cols:
        for index, row in df.iterrows():
            transaction_items = row[existing_item_cols].dropna().tolist()
            all_items.extend(transaction_items)

# If all_items is still empty, it means we couldn't find the item data
if not all_items:
    st.error("Could not find or process the item data from the CSV. Please check the column names and data format.")
    st.stop()


# --- Calculate Frequencies ---
item_counts = pd.Series(all_items).value_counts()
relative_frequency = item_counts / len(all_items)
relative_frequency_df = relative_frequency.reset_index()
relative_frequency_df.columns = ['Product', 'Relative Frequency']

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("📊 Analisi della Frequenza Relativa dei Prodotti")
st.write(f"Dataset caricato: `{file_name}`")

st.header("Frequenza Relativa dei Prodotti")

if not relative_frequency_df.empty:
    st.write("Questa tabella mostra la frequenza relativa di ciascun prodotto nel dataset.")
    st.dataframe(relative_frequency_df, height=300, use_container_width=True)

    st.header("Visualizzazione della Frequenza Relativa (Top 20 Prodotti)")
    st.write("Questo grafico a barre mostra i 20 prodotti più frequenti.")

    # Sort for better visualization and take top 20
    top_20_products = relative_frequency_df.sort_values(by='Relative Frequency', ascending=False).head(20)

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(top_20_products['Product'], top_20_products['Relative Frequency'], color='skyblue')
    ax.set_xlabel("Prodotto", fontsize=12)
    ax.set_ylabel("Frequenza Relativa", fontsize=12)
    ax.set_title("Top 20 Prodotti per Frequenza Relativa", fontsize=15)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout() # Adjust layout to prevent labels from overlapping

    # Add data labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.001, f'{yval:.3f}', ha='center', va='bottom', fontsize=8)


    st.pyplot(fig)

    st.download_button(
        label="Scarica i dati di frequenza relativa (CSV)",
        data=relative_frequency_df.to_csv(index=False).encode('utf-8'),
        file_name='frequenza_relativa_prodotti.csv',
        mime='text/csv',
    )
else:
    st.warning("Nessun dato sulla frequenza da mostrare. Controlla la colonna degli articoli nel file CSV.")

st.sidebar.header("Informazioni")
st.sidebar.info(
    "Questa applicazione analizza un dataset di generi alimentari per calcolare e visualizzare "
    "la frequenza relativa di acquisto di ciascun prodotto. "
    "I risultati sono presentati in una tabella e in un grafico a barre per i prodotti più frequenti."
)

# To run this Streamlit app:
# 1. Save the code above as a Python file (e.g., app.py).
# 2. Make sure 'Groceries_dataset.csv' is in the same directory.
# 3. Open a terminal or command prompt.
# 4. Navigate to the directory where you saved the files.
# 5. Run the command: streamlit run app.py
