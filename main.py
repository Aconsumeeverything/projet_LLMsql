import os
import psycopg2
import gradio as gr
import openai

# Configuration SambaNova OpenAI client
client = openai.OpenAI(
    api_key="8de117f4-a0bb-4d5b-80e4-5b673c4278e8",
    base_url="https://api.sambanova.ai/v1",
)


# Connexion à PostgreSQL
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="my_database",
            user="admin",
            password="admin",
            port="5432"
        )
        return conn
    except Exception as e:
        return str(e)


# Utilisation de  SambaNova pour générer une requête SQL personalisée pour que l'ia puisse intéragir avec notre  base de données
def generate_sql_sambanova(query_nl):
    prompt = f"""
You are an expert SQL assistant. Respond with only the SQL query in PostgreSQL syntax, ensuring all table and column names are double-quoted and case-sensitive.
The schema is public, and the tables are:
"Artist", "Album", "Employee", "Customer", "Invoice", "InvoiceLine", "Track", "Playlist", "PlaylistTrack", "Genre", "MediaType".

to get a better idea of the tables this is the code used to create them : 
CREATE TABLE "Album"
(
    "AlbumId" INT NOT NULL,
    "Title" VARCHAR(160) NOT NULL,
    "ArtistId" INT NOT NULL,
    CONSTRAINT "PK_Album" PRIMARY KEY  ("AlbumId")
);

CREATE TABLE "Artist"
(
    "ArtistId" INT NOT NULL,
    "Name" VARCHAR(120),
    CONSTRAINT "PK_Artist" PRIMARY KEY  ("ArtistId")
);

CREATE TABLE "Customer"
(
    "CustomerId" INT NOT NULL,
    "FirstName" VARCHAR(40) NOT NULL,
    "LastName" VARCHAR(20) NOT NULL,
    "Company" VARCHAR(80),
    "Address" VARCHAR(70),
    "City" VARCHAR(40),
    "State" VARCHAR(40),
    "Country" VARCHAR(40),
    "PostalCode" VARCHAR(10),
    "Phone" VARCHAR(24),
    "Fax" VARCHAR(24),
    "Email" VARCHAR(60) NOT NULL,
    "SupportRepId" INT,
    CONSTRAINT "PK_Customer" PRIMARY KEY  ("CustomerId")
);

CREATE TABLE "Employee"
(
    "EmployeeId" INT NOT NULL,
    "LastName" VARCHAR(20) NOT NULL,
    "FirstName" VARCHAR(20) NOT NULL,
    "Title" VARCHAR(30),
    "ReportsTo" INT,
    "BirthDate" TIMESTAMP,
    "HireDate" TIMESTAMP,
    "Address" VARCHAR(70),
    "City" VARCHAR(40),
    "State" VARCHAR(40),
    "Country" VARCHAR(40),
    "PostalCode" VARCHAR(10),
    "Phone" VARCHAR(24),
    "Fax" VARCHAR(24),
    "Email" VARCHAR(60),
    CONSTRAINT "PK_Employee" PRIMARY KEY  ("EmployeeId")
);

CREATE TABLE "Genre"
(
    "GenreId" INT NOT NULL,
    "Name" VARCHAR(120),
    CONSTRAINT "PK_Genre" PRIMARY KEY  ("GenreId")
);

CREATE TABLE "Invoice"
(
    "InvoiceId" INT NOT NULL,
    "CustomerId" INT NOT NULL,
    "InvoiceDate" TIMESTAMP NOT NULL,
    "BillingAddress" VARCHAR(70),
    "BillingCity" VARCHAR(40),
    "BillingState" VARCHAR(40),
    "BillingCountry" VARCHAR(40),
    "BillingPostalCode" VARCHAR(10),
    "Total" NUMERIC(10,2) NOT NULL,
    CONSTRAINT "PK_Invoice" PRIMARY KEY  ("InvoiceId")
);

CREATE TABLE "InvoiceLine"
(
    "InvoiceLineId" INT NOT NULL,
    "InvoiceId" INT NOT NULL,
    "TrackId" INT NOT NULL,
    "UnitPrice" NUMERIC(10,2) NOT NULL,
    "Quantity" INT NOT NULL,
    CONSTRAINT "PK_InvoiceLine" PRIMARY KEY  ("InvoiceLineId")
);

CREATE TABLE "MediaType"
(
    "MediaTypeId" INT NOT NULL,
    "Name" VARCHAR(120),
    CONSTRAINT "PK_MediaType" PRIMARY KEY  ("MediaTypeId")
);

CREATE TABLE "Playlist"
(
    "PlaylistId" INT NOT NULL,
    "Name" VARCHAR(120),
    CONSTRAINT "PK_Playlist" PRIMARY KEY  ("PlaylistId")
);

CREATE TABLE "PlaylistTrack"
(
    "PlaylistId" INT NOT NULL,
    "TrackId" INT NOT NULL,
    CONSTRAINT "PK_PlaylistTrack" PRIMARY KEY  ("PlaylistId", "TrackId")
);

CREATE TABLE "Track"
(
    "TrackId" INT NOT NULL,
    "Name" VARCHAR(200) NOT NULL,
    "AlbumId" INT,
    "MediaTypeId" INT NOT NULL,
    "GenreId" INT,
    "Composer" VARCHAR(220),
    "Milliseconds" INT NOT NULL,
    "Bytes" INT,
    "UnitPrice" NUMERIC(10,2) NOT NULL,
    CONSTRAINT "PK_Track" PRIMARY KEY  ("TrackId")
);

Examples:
- User's query: "List all artist names."
  SQL query: SELECT "Name" FROM public."Artist";

- User's query: "Get all albums released by artist ID 5."
  SQL query: SELECT * FROM public."Album" WHERE "ArtistId" = 5;

User's query: "{query_nl}"
SQL query:
"""
    try:
        response = client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": "You are a helpful SQL assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1
        )
        sql_query = response.choices[0].message.content.strip()
        
      
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return sql_query
    except Exception as e:
        return f"Erreur lors de la génération SQL : {str(e)}"


# Exécuter la requête SQL sur PostgreSQL
def execute_query(sql_query):
    conn = connect_to_postgres()
    if isinstance(conn, str): 
        return f"Erreur de connexion : {conn}"

    cursor = conn.cursor()

    try:
        cursor.execute(sql_query)
        if cursor.description:  
            columns = [desc[0] for desc in cursor.description] 
            rows = cursor.fetchall()  
            result = [columns] + rows  
            return result
        else:
            conn.commit()
            return "Requête exécutée avec succès sans retour de données."
    except Exception as e:
        return f"Erreur lors de l'exécution : {str(e)}"
    finally:
        cursor.close()
        conn.close()


def query_interface(query_nl):
    sql_query = generate_sql_sambanova(query_nl)
    if sql_query.startswith("Erreur"):
        return sql_query, "SQL generation failed."

    # Executer la requette générée par l IA
    result = execute_query(sql_query)
    if isinstance(result, list):  # Result is a table
        formatted_result = "\n".join(
            [", ".join(map(str, row)) for row in result]
        )
        return sql_query, formatted_result
    return sql_query, result


# l'interface Gradio 
iface = gr.Interface(
    fn=query_interface,
    inputs=gr.Textbox(
        label="Question en langage naturel",
        placeholder="Exemple : Listez tous les noms d'artistes.",
        lines=5,  # Increase the number of lines for the input box
    ),
    outputs=[
        gr.Textbox(label="SQL Query utilisée", lines=7),  # Bigger box for SQL query
        gr.Textbox(label="Résultat de la requête", lines=15),  # Bigger box for query result
    ],
    title="Générateur et Exécuteur de Requêtes SQL basé sur LLM",
    description=(
        "Posez une question en langage naturel, et le modèle génère une requête SQL "
        "et l'exécute sur votre base de données PostgreSQL. "
        "Les résultats sont affichés ci-dessous."
    ),
    examples=[
        ["List all artist names."],
        ["List all the albums"],
        ["Show all employees."],
    ],
    theme="default",
    css="style.css",  
)


iface.launch()
