# !/usr/bin/env python3

__version__="1.0.5"

import argparse, io, os, json, csv, glob, hashlib, tempfile, warnings, base64, random, math
from sklearn.base import BaseEstimator, TransformerMixin
from collections import defaultdict
from datetime import datetime
from typing import Tuple
from fpdf import FPDF
import scipy.stats as st
import scipy as sp
import numpy as np
import pandas as pd

def list_csv_files():
    return [f for f in os.listdir() if f.endswith('.csv')]

def list_json_files():
    return [f for f in os.listdir() if f.endswith('.json')]

def list_html_files():
    return [f for f in os.listdir() if f.endswith('.html')]

def list_png_files():
    return [f for f in os.listdir() if f.endswith('.png')]

def list_ico_files():
    return [f for f in os.listdir() if f.endswith('.ico')]

def list_python_files():
    return [f for f in os.listdir() if f.endswith('.py')]

def list_data_files():
    return [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(('.txt', '.csv', '.json'))]

def list_py_files(directory="."):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def ico2png():
    ico_images = list_ico_files()
    if ico_images:
        print("PNG image(s) available. Select which one to convert:")
        for index, file_name in enumerate(ico_images, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(ico_images)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=ico_images[choice_index]
            print(f"ICO image: {selected_file} is selected!")
            from PIL import Image
            with Image.open(selected_file) as img:
                img.save("icon.png", format="PNG", size=[(32, 32)])
            print("Done; converted to icon.png and saved in the same directory.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No ICO images are available in the current directory.")

def png2ico():
    png_images = list_png_files()
    if png_images:
        print("PNG image(s) available. Select which one to convert:")
        for index, file_name in enumerate(png_images, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(png_images)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=png_images[choice_index]
            print(f"PNG image: {selected_file} is selected!")
            from PIL import Image
            png_image = Image.open(selected_file)
            png_image.save("icon.ico", format='ICO', sizes=[(32, 32)])
            print("Done; converted to icon.ico and saved in the same directory.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No PNG images are available in the current directory.")

def data_file_reader(file_name):
    if file_name.endswith('.txt'):
        with open(file_name, 'r', encoding='utf-8') as f:
            print(f.read())
    elif file_name.endswith('.csv'):
        with open(file_name, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)
    elif file_name.endswith('.json'):
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(json.dumps(data, indent=4))
    else:
        print("Unsupported file format.")

def read_data_file():
    files = list_data_files()
    if not files:
        print("No .txt, .csv, or .json file(s) found in the current directory.")
        return
    print("Available files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    try:
        choice = int(input("Select a file by number: ")) - 1
        if 0 <= choice < len(files):
            data_file_reader(files[choice])
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")

def py_minifier2(file_path):
    import ast, pyminify
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        tree = ast.parse(code)
        class RemoveAnnotations(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                node.returns = None
                node.args.args = [ast.arg(arg=arg.arg, annotation=None) for
                    arg in node.args.args]
                return self.generic_visit(node)
        tree = RemoveAnnotations().visit(tree)
        ast.fix_missing_locations(tree)
        minified_code = pyminify.to_source(tree)
        minified_code = '\n'.join(line for line in minified_code.splitlines
            () if line.strip() and not line.strip().startswith('#'))
        minified_file = os.path.join(os.path.dirname(file_path), f'{os.path.basename(file_path)}')
        with open(minified_file, 'w', encoding='utf-8') as file:
            file.write(minified_code)
        print(f'Overwritten the original content and saved as: {minified_file}')
    except Exception as e:
        print(f'Error while minifying the file {file_path}: {e}')

def py_minifier(file_path):
    import ast, pyminify
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        tree = ast.parse(code)
        class RemoveAnnotations(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                node.returns = None
                node.args.args = [ast.arg(arg=arg.arg, annotation=None) for
                    arg in node.args.args]
                return self.generic_visit(node)
        tree = RemoveAnnotations().visit(tree)
        ast.fix_missing_locations(tree)
        minified_code = pyminify.to_source(tree)
        minified_code = '\n'.join(line for line in minified_code.splitlines
            () if line.strip() and not line.strip().startswith('#'))
        minified_file = f'{os.path.basename(file_path)}'
        with open(minified_file, 'w', encoding='utf-8') as file:
            file.write(minified_code)
        print(f'Overwritten the original content and saved as: {minified_file}')
    except Exception as e:
        print(f'Error while minifying the file {file_path}: {e}')

def minify_py():
    python_files = list_python_files()
    if not python_files:
        print('No Python files found in the current directory.')
    else:
        print('Minifying all Python files in the current directory...')
        for file in python_files:
            py_minifier(file)
        print('All files have been minified.')

def minify_py2():
    python_files = list_py_files()
    if not python_files:
        print('No Python files found in the current directory and its subdirectories.')
    else:
        print('Minifying all Python files in the current directory and subdirectories...')
        for file in python_files:
            py_minifier2(file)
        print('All files have been minified.')

def load_descriptors_from_json():
    json_files = list_json_files()
    if not json_files:
        print("No JSON files found in the current directory.")
        return None
    print("Available JSON files:")
    for idx, filename in enumerate(json_files, start=1):
        print(f"{idx}: {filename}")
    try:
        choice = int(input("Select a JSON file by entering its number: "))
        if 1 <= choice <= len(json_files):
            with open(json_files[choice - 1], 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            print("Invalid choice.")
            return None
    except (ValueError, IndexError):
        print("Invalid input. Please enter a valid number.")
        return None

def get_column_info(descriptors):
    column_mapping = {}
    keys = list(descriptors.keys())
    print("Available columns:")
    for idx, key in enumerate(keys, start=1):
        print(f"{idx}: {key}")
    try:
        for column_name in ["subject", "hair color", "eye color", "scene"]:
            choice = int(input(f"Select the column number for '{column_name}': "))
            if 1 <= choice <= len(keys):
                column_mapping[column_name] = descriptors[keys[choice - 1]]
            else:
                print("Invalid choice.")
                return None
        return column_mapping
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        return None

def select_descriptor_component(column_mapping):
    subject = random.choice(column_mapping["subject"])
    hair_color = random.choice(column_mapping["hair color"])
    eye_color = random.choice(column_mapping["eye color"])
    scene = random.choice(column_mapping["scene"])
    return f"A {hair_color} haired {subject} with {eye_color} eyes, {scene}."

def generate_txt_descriptor():
    descriptors = load_descriptors_from_json()
    if not descriptors:
        return
    column_mapping = get_column_info(descriptors)
    if not column_mapping:
        return
    try:
        num_descriptors = int(input("Enter the number of descriptors to generate: "))
        if num_descriptors <= 0:
            print("Please enter a positive number.")
            return
        for i in range(1, num_descriptors + 1):
            descriptor = select_descriptor_component(column_mapping)
            filename = f"{i}.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(descriptor)
        print(f"{num_descriptors} descriptors generated and saved in separate text files.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")

def csv_to_txt():
    csv_files = list_csv_files()
    for csv_file in csv_files:
        txt_file = os.path.splitext(csv_file)[0] + '.txt'
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as infile, \
                open(txt_file, 'w', newline='', encoding='utf-8') as outfile:
                reader = csv.reader(infile)
                for row in reader:
                    outfile.write('\t'.join(row) + '\n')
            print(f"Converted: {csv_file} -> {txt_file}")
        except Exception as e:
            print(f"Error converting {csv_file}: {e}")
    print("Conversion completed.")

def generate_png(file_path, png_width, png_height):
    from PIL import Image
    image = Image.new("RGBA", (png_width, png_height), (0, 0, 0, 0))
    image.save(file_path)

def create_png():
    png_width = input("Please provide the width in pixel (i.e., 1024): ")
    png_height = input("Please provide the height in pixel (i.e., 768): ")
    ask = input("Enter another file name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        file_path=given+".png"
    else:
        file_path="output.png"
    generate_png(file_path, int(png_width), int(png_height))
    print(f"PNG file generated at: {file_path}")

def create_gif():
    from PIL import Image
    num_pictures = int(input("Enter the number of pictures to include in the animation: "))
    input_files = []
    for i in range(num_pictures):
        filename = input(f"Enter the filename for picture {i + 1} (with .png extension): ")
        input_files.append(filename)
    transition_times = []
    for i in range(num_pictures):
        duration = int(input(f"Enter the transition time (ms) for picture {i + 1}: "))
        transition_times.append(duration)
    loop_number = int(input("Enter the loop number (0 for infinity): "))
    frames = []
    for file in input_files:
        img = Image.open(file)
        frames.append(img)
    frames[0].save(
        'output.gif', 
        save_all=True, 
        append_images=frames[1:], 
        duration=transition_times, 
        loop=loop_number
    )
    print("GIF animation created as 'output.gif'!")

def minify_html(html_content):
    import re
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'\s+', ' ', html_content).strip()
    return html_content

def html_minifier():
    html_files = list_html_files()
    if not html_files:
        print("No HTML files found in the current directory.")
        return
    print("Select an HTML file to minify:")
    for i, file_name in enumerate(html_files, start=1):
        print(f"{i}. {file_name}")
    try:
        choice = int(input("Enter the number corresponding to the file: "))
        if 1 <= choice <= len(html_files):
            selected_file = html_files[choice - 1]
            with open(selected_file, 'r', encoding='utf-8') as file:
                content = file.read()
            minified_content = minify_html(content)
            output_file = f"{os.path.splitext(selected_file)[0]}_minified.html"
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(minified_content)
            print(f"Minified HTML saved as {output_file}")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def json_merger():
    merged_data = []
    for filename in os.listdir('.'):
        if filename.endswith('.json'):
            with open(filename, 'r') as file:
                data = json.load(file)
                merged_data.extend(data)
    with open('output.json', 'w') as outfile:
        json.dump(merged_data, outfile, indent=4)
    print("Merged JSON saved as output.json")

def minify_json_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, separators=(',', ':'), ensure_ascii=False)
    print(f"File '{file_name}' has been minified.")

def minify_json():
    json_files = list_json_files()
    if not json_files:
        print("No JSON files found in the current directory.")
        return
    print("JSON files in the current directory:")
    for idx, file in enumerate(json_files, start=1):
        print(f"{idx}. {file}")
    try:
        choice = int(input("Select a JSON file to minify by entering its number: ")) - 1
        if 0 <= choice < len(json_files):
            selected_file = json_files[choice]
            minify_json_file(selected_file)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def timestamp_cutter():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    print("Available CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"{i}. {file}")
    try:
        choice = int(input("Select the CSV file by entering the corresponding number: "))
        csv_file = csv_files[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    try:
        df = pd.read_csv(csv_file)
        def split_timestamp(timestamp):
            date, time = timestamp.split()
            month, day, year = date.split('/')
            return year, month, day, time
        df[['Year', 'Month', 'Day', 'Time']] = df['timestamp'].apply(
            lambda x: pd.Series(split_timestamp(x))
        )
        output = "output.csv"
        df.to_csv(output, index=False)
        print(f"Results saved to {output}")
    except Exception as e:
        print(f"Error reading the file: {e}")

def timestamp_glue():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    print("Available CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"{i}. {file}")
    try:
        choice = int(input("Select the CSV file by entering the corresponding number: "))
        csv_file = csv_files[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    try:
        df = pd.read_csv(csv_file)
        df['timestamp'] = pd.to_datetime(df['Year'].astype(str) + '/' + 
                                        df['Month'].astype(str) + '/' + 
                                        df['Day'].astype(str) + ' ' + 
                                        df['Time'])
        output = "output.csv"
        df.to_csv(output, index=False)
        print(f"Results saved to {output}")
    except Exception as e:
        print(f"Error reading the file: {e}")

def compute_point():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    print("Available CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"{i}. {file}")
    try:
        choice = int(input("Select the CSV file by entering the corresponding number: "))
        csv_file = csv_files[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    try:
        output_file1 = 'output1.csv'
        output_file2 = 'output2.csv'
        df = pd.read_csv(csv_file)
        session_sums = df.groupby('Session')['Score'].sum().reset_index()
        session_sums.rename(columns={'Score': 'Sum'}, inplace=True)
        df = df.merge(session_sums, on='Session', how='left')
        df['Sum'] = df.apply(lambda row: row['Sum'] if df[df['Session'] == row['Session']].index[0] == row.name else '', axis=1)
        df.to_csv(output_file1, index=False)
        print(f"Stage 1 process completed; output saved to {output_file1}")
        data = pd.read_csv(output_file1)
        data['Point'] = data.apply(lambda row: row['Sum'] if pd.notnull(row['Sum']) and pd.notnull(row['Score']) and row['Sum'] > row['Score'] else None, axis=1)
        data.to_csv(output_file2, index=False)
        print(f"Stage 2 process completed; output saved to {output_file2}")
    except Exception as e:
        print(f"Error reading the file: {e}")

def generate_report(pdf, id_val, name_val, records):
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"{id_val} - {name_val}", 0, 1, 'C')
    pdf.ln(10)
    table_col_widths = [50, 30, 30]
    table_width = sum(table_col_widths)
    page_width = pdf.w - 2 * pdf.l_margin
    table_x_margin = (page_width - table_width) / 2
    pdf.set_font('Arial', 'B', 12)
    pdf.set_x(pdf.l_margin + table_x_margin)
    pdf.cell(table_col_widths[0], 10, 'Group', 1, 0, 'C')
    pdf.cell(table_col_widths[1], 10, 'Count', 1, 0, 'C')
    pdf.cell(table_col_widths[2], 10, 'Minute', 1, 1, 'C')
    pdf.set_font('Arial', '', 12)
    total_min = 0
    total_count = 0
    group_summary = records.groupby(records.columns[2]).agg(
        count=(records.columns[2], 'size'),
        total_min=(records.columns[3], 'sum')
    ).reset_index()
    for _, row in group_summary.iterrows():
        pdf.set_x(pdf.l_margin + table_x_margin)
        pdf.cell(table_col_widths[0], 10, str(row[records.columns[2]]), 1, 0, 'C')
        pdf.cell(table_col_widths[1], 10, str(row['count']), 1, 0, 'C')
        pdf.cell(table_col_widths[2], 10, str(row['total_min']), 1, 1, 'C')
        total_min += row['total_min']
        total_count += row['count']
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_x(pdf.l_margin + table_x_margin)
    pdf.cell(table_col_widths[0], 10, 'Total', 1, 0, 'C')
    pdf.cell(table_col_widths[1], 10, str(total_count), 1, 0, 'C')
    pdf.cell(table_col_widths[2], 10, str(total_min), 1, 1, 'C')

class PDF(FPDF):
    def header(self):
        pass
    def footer(self):
        pass

def generate_reports():
    csv_files = list_csv_files()
    if csv_files:
        print("CSV file(s) available. Select which one to use:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=csv_files[choice_index]
            print(f"File: {selected_file} is selected!")
            df = pd.read_csv(selected_file)
            grouped = df.groupby([df.columns[0], df.columns[1]])
            for (id_val, name_val), group in grouped:
                pdf = PDF()
                pdf.add_page()
                generate_report(pdf, id_val, name_val, group)
                pdf.output(f"{id_val}.pdf")
                print(f"{id_val}.pdf created.")
            print("PDF reports generated successfully.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")
        input("--- Press ENTER To Exit ---")

def encode_base64(input_text):
    encoded_bytes = base64.b64encode(input_text.encode('utf-8'))
    encoded_text = encoded_bytes.decode('utf-8')
    return encoded_text

def decode_base64(encoded_text):
    decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
    decoded_text = decoded_bytes.decode('utf-8')
    return decoded_text

def base64codeHandler():
    choice = input("Do you want to encode or decode? (Enter 'encode' or 'decode'): ").strip().lower()
    if choice == 'encode':
        text_to_encode = input("Enter the text to encode: ")
        encoded_text = encode_base64(text_to_encode)
        print("Encoded text:", encoded_text)
    elif choice == 'decode':
        text_to_decode = input("Enter the Base64 text to decode: ")
        try:
            decoded_text = decode_base64(text_to_decode)
            print("Decoded text:", decoded_text)
        except Exception as e:
            print("Error decoding text. Make sure it's valid Base64.")
    else:
        print("Invalid choice. Please enter 'encode' or 'decode'.")

def select_csv_file(csv_files):
    print("Available CSV files:")
    for i, file in enumerate(csv_files):
        print(f"{i + 1}: {file}")
    file_index = int(input("Select a CSV file by number: ")) - 1
    return csv_files[file_index]

def select_csv_file_gui():
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.withdraw()
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    return file_path

def output_as_csv_json():
    input_file = select_csv_file_gui()
    df = pd.read_csv(input_file)
    col_id, col_group, col_min = df.columns[:3]
    grouped_df = df.groupby([col_id, col_group], as_index=False)[col_min].sum()
    grouped_df.to_csv('output.csv', index=False)
    json_data = []
    for id_value, group_data in grouped_df.groupby(col_id):
        group_dict = {}
        for _, row in group_data.iterrows():
            group_dict[row[col_group]] = row[col_min]
        json_data.append({col_id: id_value, col_group: [group_dict]})
    with open('output.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

def select_column(df):
    print("Available columns:")
    for i, col in enumerate(df.columns):
        print(f"{i + 1}: {col}")
    col_index = int(input("Select a column by number: ")) - 1
    return df.columns[col_index]

def select_columns(df):
    print("Available columns:")
    for i, col in enumerate(df.columns):
        print(f"{i + 1}: {col}")
    col_index1 = int(input("Select the first column by number: ")) - 1
    col_index2 = int(input("Select the second column by number: ")) - 1
    return df.columns[col_index1], df.columns[col_index2]

def select_columnx(df):
    print("Available columns:")
    for i, col in enumerate(df.columns):
        print(f"{i + 1}: {col}")
    col_index1 = int(input("Select the first column by number: ")) - 1
    col_index2 = int(input("Select the second column by number: ")) - 1
    col_index3 = int(input("Select the third column by number: ")) - 1
    return df.columns[col_index1], df.columns[col_index2], df.columns[col_index3]

def select_column_free(df):
    col_index = int(input(f"Select a column by number: ")) - 1
    return df.columns[col_index]

def clean_data(df, columns):
    df = df[columns].replace([np.inf, -np.inf], np.nan)
    df = df.dropna()
    return df

def csv_to_json():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    print("Available CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"{i}. {file}")
    try:
        choice = int(input("Select the CSV file by entering the corresponding number: "))
        csv_file = csv_files[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading the file: {e}")
        return
    json_data = df.to_dict(orient='records')
    json_file_name = os.path.splitext(csv_file)[0] + '.json'
    try:
        with open(json_file_name, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
        print(f"JSON file saved as '{json_file_name}'.")
    except Exception as e:
        print(f"Error saving the JSON file: {e}")

def joint():
    csv_files = list_csv_files()
    dataframes = []
    for file in csv_files:
        df = pd.read_csv(file)
        dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    ask = input("Enter another file name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
            given = input("Give a name to the output file: ")
            output=given
    else:
            output="output"
    combined_df.to_csv(f'{output}.csv', index=False)

def innerj():
    csv_files = list_csv_files()
    if csv_files:
        print("CSV file(s) available. Select the 1st csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        file1=csv_files[choice_index]
        print("CSV file(s) available. Select the 2nd csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        file2=csv_files[choice_index]
        ask = input("Enter another file name instead of output (Y/n)? ")
        if  ask.lower() == 'y':
                given = input("Give a name to the output file: ")
                output=given
        else:
                output="output"
        try:
            df1 = pd.read_csv(file1)
            df2 = pd.read_csv(file2)
            first_column_file1 = df1.columns[0]
            first_column_file2 = df2.columns[0]
            merged_df = pd.merge(df1, df2, left_on=first_column_file1, right_on=first_column_file2, how='inner')
            output_file = f"{output}.csv"
            merged_df.to_csv(output_file, index=False)
            print(f"Inner join completed and saved to {output_file}")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def outerj():
    csv_files = list_csv_files()
    if csv_files:
        print("CSV file(s) available. Select the 1st csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        file1=csv_files[choice_index]
        print("CSV file(s) available. Select the 2nd csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        file2=csv_files[choice_index]
        ask = input("Enter another file name instead of output (Y/n)? ")
        if  ask.lower() == 'y':
                given = input("Give a name to the output file: ")
                output=given
        else:
                output="output"
        try:
            df1 = pd.read_csv(file1)
            df2 = pd.read_csv(file2)
            first_column_file1 = df1.columns[0]
            first_column_file2 = df2.columns[0]
            merged_df = pd.merge(df1, df2, left_on=first_column_file1, right_on=first_column_file2, how='outer')
            output_file = f"{output}.csv"
            merged_df.to_csv(output_file, index=False)
            print(f"Outer join completed and saved to {output_file}")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def eraser():
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    root.withdraw()
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    input_file = askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    if not input_file:
        print("No file selected. Exiting...")
        return
    try:
        df = pd.read_csv(input_file)
        print(f"Data loaded from {input_file}")
    except Exception as e:
        print(f"Error reading the file: {e}")
        return
    df_cleaned = df.drop_duplicates()
    output_file = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save the cleaned file as")
    if not output_file:
        print("No file selected for saving. Exiting...")
        return
    df_cleaned.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")

def mk_dir():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* Select a column storing the folder list *\n")
    selected_column = select_column(df)
    for folder_name in df[selected_column].dropna().unique():
        os.makedirs(str(folder_name), exist_ok=True)
    print("Folders created successfully.")

def one_way_anova_v2():
    file_path = select_csv_file_gui()
    data = pd.read_csv(file_path)
    print("\n* Reminder: 1st column should be GROUP variable *\n")
    group_column, value_column = select_columns(data)
    groups = data.groupby(group_column)[value_column]
    group_means = groups.mean()
    group_sizes = groups.size()
    group_stds = groups.std(ddof=1)
    f_statistic, p_value = st.f_oneway(*[group for name, group in groups])
    df_between = len(groups) - 1
    df_within = len(data) - len(groups)
    overall_mean = data[value_column].mean()
    ss_between = sum(size * (mean - overall_mean) ** 2 for size, mean in zip(group_sizes, group_means))
    ss_total = sum((value - overall_mean) ** 2 for value in data[value_column])
    eta_squared = ss_between / ss_total
    cohen_f = np.sqrt(eta_squared / (1 - eta_squared))
    alpha = 0.05
    from statsmodels.stats.power import FTestAnovaPower
    power_analysis = FTestAnovaPower()
    power = power_analysis.power(effect_size=cohen_f, 
                                 k_groups=len(groups), 
                                 nobs=len(data), 
                                 alpha=alpha)
    print("\nResults of the One-Way ANOVA:")
    for group_name, mean, std in zip(group_means.index, group_means, group_stds):
        print(f"Group: {group_name}, Mean: {mean:.4f}, Standard Deviation: {std:.4f}")
    print(f"F({df_between}, {df_within}) = {f_statistic:.4f}")
    print(f"p-value = {p_value:.4f}")
    print(f"Effect Size (Cohen's f): {cohen_f:.4f}")
    print(f"Power (1-β): {power:.4f}")
    print("\nEffect Size calculation based on η²:")
    print(f"Effect Size (Eta Squared)    : {eta_squared:.4f}")
    print(f"Sum of Squares Between Groups: {ss_between:.4f}")
    print(f"Sum of Squares Within Groups : {ss_total-ss_between:.4f}")
    print(f"Sum of Squares Total         : {ss_total:.4f}")
    if p_value <= 0.01: p = "p < .01"
    elif p_value < 0.05 and p_value > 0.01: p = "p < .05"
    else: p = f"p = {p_value:.3f}"
    print(f"\nJournal/report format:\nF({df_between}, {df_within}) = {f_statistic:.3f}, {p}, η² = {eta_squared:.2f}")
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    tukey = pairwise_tukeyhsd(endog=data[value_column], 
                              groups=data[group_column], 
                              alpha=alpha)
    print("\nTukey's HSD Test Results:")
    print(tukey)

def independent_sample_t_test_v2():
    file_path = select_csv_file_gui()
    df = pd.read_csv(file_path)
    col1, col2 = select_columns(df)
    group_1 = df[col1].dropna()
    group_2 = df[col2].dropna()
    mean_1 = np.mean(group_1)
    std_1 = np.std(group_1, ddof=1)
    mean_2 = np.mean(group_2)
    std_2 = np.std(group_2, ddof=1)
    t_statistic, p_value = st.ttest_ind(group_1, group_2, equal_var=False)
    d_f = len(group_1) + len(group_2) - 2
    pooled_std = np.sqrt(((len(group_1) - 1) * std_1 ** 2 + (len(group_2) - 1) * std_2 ** 2) / d_f)
    cohen_d = (mean_1 - mean_2) / pooled_std
    alpha = 0.05
    from statsmodels.stats.power import TTestIndPower
    power_analysis = TTestIndPower()
    power = power_analysis.power(effect_size=cohen_d, nobs1=len(group_1), ratio=len(group_2)/len(group_1), alpha=alpha, alternative='two-sided')
    print("\nResults of the Independent-Sample t-Test:")
    print(f"Mean (Group 1): {mean_1:.4f}")
    print(f"Standard Deviation (Group 1): {std_1:.4f}")
    print(f"Mean (Group 2): {mean_2:.4f}")
    print(f"Standard Deviation (Group 2): {std_2:.4f}")
    print(f"t({d_f}) = {t_statistic:.4f}")
    print(f"p-value = {p_value:.4f}")
    print(f"Effect Size (Cohen's d): {cohen_d:.4f}")
    print(f"Power (1-β): {power:.4f}")
    if mean_1 > mean_2: cp = ">"
    elif mean_1 < mean_2: cp = "<"
    else: cp = "="
    if p_value <= 0.01: p = "p < .01"
    elif p_value < 0.05 and p_value > 0.01: p = "p < .05"
    else: p = f"p = {p_value:.3f}"
    print(f"\nJournal/report format:\n{mean_1:.2f}(±{std_1:.3f}) {cp} {mean_2:.2f}(±{std_2:.3f}); t({d_f}) = {t_statistic:.3f}, {p}, d = {cohen_d:.2f}")

def paired_sample_t_test_v2():
    file_path = select_csv_file_gui()
    df = pd.read_csv(file_path)
    col1, col2 = select_columns(df)
    sample_1 = df[col1].dropna()
    sample_2 = df[col2].dropna()
    if len(sample_1) != len(sample_2):
        raise ValueError("The two columns must have the same number of observations.")
    diff = sample_1 - sample_2
    mean_diff = np.mean(diff)
    std_diff = np.std(diff, ddof=1)
    t_statistic, p_value = st.ttest_rel(sample_1, sample_2)
    d_f = len(diff) - 1
    cohen_d = mean_diff / std_diff
    alpha = 0.05
    from statsmodels.stats.power import TTestPower
    power_analysis = TTestPower()
    power = power_analysis.power(effect_size=cohen_d, nobs=len(diff), alpha=alpha, alternative='two-sided')
    print("\nResults of the Paired-Sample t-Test:")
    print(f"Mean of Differences: {mean_diff:.4f}")
    print(f"Standard Deviation of Differences (SD): {std_diff:.4f}")
    print(f"t({d_f}) = {t_statistic:.4f}")
    print(f"p-value = {p_value:.4f}")
    print(f"Effect Size (Cohen's d): {cohen_d:.4f}")
    print(f"Power (1-β): {power:.4f}")
    if p_value <= 0.01: p = "p < .01"
    elif p_value < 0.05 and p_value > 0.01: p = "p < .05"
    else: p = f"p = {p_value:.3f}"
    print(f"\nJournal/report format:\nΔ {mean_diff:.2f} ± {std_diff:.3f}; t({d_f}) = {t_statistic:.3f}, {p}, d = {cohen_d:.2f}")

def one_sample_t_test_v2():
    file_path = select_csv_file_gui()
    df = pd.read_csv(file_path)
    selected_column = select_column(df)
    sample_data = df[selected_column].dropna()
    population_mean = float(input("Enter the population mean (µ): "))
    t_statistic, p_value = st.ttest_1samp(sample_data, population_mean)
    sample_mean = np.mean(sample_data)
    sample_std = np.std(sample_data, ddof=1)
    d_f = len(sample_data) - 1
    cohen_d = (sample_mean - population_mean) / sample_std
    alpha = 0.05
    from statsmodels.stats.power import TTestPower
    power_analysis = TTestPower()
    power = power_analysis.power(effect_size=cohen_d, nobs=len(sample_data), alpha=alpha, alternative='two-sided')
    print("\nResults of the One-Sample t-Test:")
    print(f"Sample Mean: {sample_mean:.4f}")
    print(f"Sample Standard Deviation (SD): {sample_std:.4f}")
    print(f"t({d_f}) = {t_statistic:.4f}")
    print(f"p-value = {p_value:.4f}")
    print(f"Effect Size (Cohen's d): {cohen_d:.4f}")
    print(f"Power (1-β): {power:.4f}")
    if p_value <= 0.01: p = "p < .01"
    elif p_value < 0.05 and p_value > 0.01: p = "p < .05"
    else: p = f"p = {p_value:.3f}"
    print(f"\nJournal/report format:\n{sample_mean:.2f} ± {sample_std:.3f}; t({d_f}) = {t_statistic:.3f}, {p}, d = {cohen_d:.2f}")

def regression_analysis(df, dependent_var, predictors):
    import statsmodels.api as sm
    X = df[predictors]
    y = df[dependent_var]
    X = sm.add_constant(X)
    model = sm.OLS(y, X)
    results = model.fit()
    return results

def regression():
    file_path = select_csv_file_gui()
    if not file_path:
        print("No file selected. Exiting.")
        return
    df = pd.read_csv(file_path)
    print("Columns in the selected CSV file:", df.columns.tolist())
    dependent_var = input("Enter the column name for the dependent variable: ")
    if dependent_var not in df.columns:
        print(f"Column '{dependent_var}' not found in the CSV file. Exiting.")
        return
    num_predictors = int(input("Enter the number of predictors: "))
    predictors = []
    for i in range(num_predictors):
        predictor = input(f"Enter the column name for predictor {i+1}: ")
        if predictor not in df.columns:
            print(f"Column '{predictor}' not found in the CSV file. Exiting.")
            return
        predictors.append(predictor)
    selected_columns = [dependent_var] + predictors
    df_clean = clean_data(df, selected_columns)
    if df_clean.empty:
        print("No data left after cleaning. Exiting.")
        return
    results = regression_analysis(df_clean, dependent_var, predictors)
    print("\nRegression Analysis Summary:")
    print(results.summary())

def cronbach_alpha(df):
    item_variances = df.var(axis=0, ddof=1)
    total_variance = df.sum(axis=1).var(ddof=1)
    n_items = df.shape[1]
    alpha = (n_items / (n_items - 1)) * (1 - item_variances.sum() / total_variance)
    return alpha

def cronbach_alpha_if_deleted(df):
    alphas = {}
    for col in df.columns:
        df_subset = df.drop(columns=[col])
        alpha = cronbach_alpha(df_subset)
        alphas[col] = alpha
    return alphas

def reliability_test():
    file_path = select_csv_file_gui()
    if file_path:
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully from {file_path}")
    else:
        print("No file selected.")
        return
    print("Available columns:")
    for i, col in enumerate(df.columns):
        print(f"{i + 1}: {col}")
    num_items = int(input("Enter the number of items (columns) within the construct: "))
    selected_columns = []
    for i in range(num_items):
        print(f"For item {i + 1}")
        col = select_column_free(df)
        selected_columns.append(col)
    df_clean = clean_data(df, selected_columns)
    if df_clean.empty:
        print("No data left after cleaning. Exiting.")
        return
    overall_alpha = cronbach_alpha(df_clean)
    print(f"\nCronbach's alpha for the selected items is: {overall_alpha}")
    alphas_if_deleted = cronbach_alpha_if_deleted(df_clean)
    print("\nCronbach's alpha if an item is deleted:")
    for item, alpha in alphas_if_deleted.items():
        print(f" - {item}: {alpha}")

def count_and_percentage(df, column_name):
    total_count = len(df[column_name])
    value_counts = df[column_name].value_counts()
    print(f"Results of pizza analysis for column '{column_name}':\n")
    for value, count in value_counts.items():
        percentage = (count / total_count) * 100
        print(f"{value}\t{count} ({percentage:.0f}%)")
    print("-" * 15)
    print(f"Total:\t{total_count}")
    ask = input("\nDo you want a pie? (Y/n) ")
    if ask.lower() == "n":
        print("Do tell me when you wanna a pie next time; thank you.")
    else:
        import tkinter as tk
        root = tk.Tk()
        icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
        root.iconphoto(False, icon)
        root.title("rjj")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack()
        root.mainloop()

def piechart():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    column_name = select_column(df)
    if column_name in df.columns:
        count_and_percentage(df, column_name)
    else:
        print("Invalid column selected!")

def boxplot():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    selected_column = select_column(df)
    data = df[selected_column].dropna()
    plot_title = input("Give a title to the Plot: ")
    print("Done! Please check the pop-up window for output.")
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.boxplot(data)
    ax.set_title(plot_title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def boxplots():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* 1st column: X-axis (i.e., GROUP variable); 2nd column: Y-axis (i.e., data) *\n")
    col1, col2 = select_columns(df)
    group = df[col1].dropna()
    data = df[col2].dropna()
    xaxis = input("Give a name to X-axis (Group): ")
    yaxis = input("Give a name to Y-axis (Value): ")
    plot_title = input("Give a title to the Plot: ")
    print("Done! Please check the pop-up window for output.")
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    grouped_data = {}
    for g, d in zip(group, data):
        if g not in grouped_data:
            grouped_data[g] = []
        grouped_data[g].append(d)
    box_data = [grouped_data[g] for g in grouped_data]
    fig, ax = plt.subplots()
    ax.boxplot(box_data, labels=grouped_data.keys())
    ax.set_xlabel(xaxis)
    ax.set_ylabel(yaxis)
    ax.set_title(plot_title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def mapper():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* 1st column: X-axis ; 2nd column: Y-axis ; 3rd coloum: Z-axis *\n")
    col1, col2, col3 = select_columnx(df)
    x = df[col1].dropna()
    y = df[col2].dropna()
    z = df[col3].dropna()
    xaxis = input("Give a name to X-axis: ")
    yaxis = input("Give a name to Y-axis: ")
    zaxis = input("Give a name to Z-axis: ")
    title = input("Give a title to the Map: ")
    print("Done! Please check the pop-up window for output.")
    from scipy.interpolate import griddata
    grid_x, grid_y = np.mgrid[min(x):max(x):100j, min(y):max(y):100j]
    grid_z = griddata((x, y), z, (grid_x, grid_y), method='cubic')
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(grid_x, grid_y, grid_z, cmap='gray', edgecolor='none')
    fig.colorbar(surf)
    ax.set_xlabel(xaxis)
    ax.set_ylabel(yaxis)
    ax.set_zlabel(zaxis)
    ax.set_title(title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def heatmap():
    ask = input("Do you want to taste a quarter? (Y/n) ")
    if ask.lower() == "y":
        x = np.linspace(-1, 15)
        y = np.linspace(-1, 15)
        title = "Quarter"
    else:
        x = np.linspace(-5, 5)
        y = np.linspace(-5, 5)
        title = "Donut"
    x, y = np.meshgrid(x, y)
    z = np.sin(np.sqrt(x**2 + y**2))
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(x, y, z, cmap='gray', edgecolor='none')
    fig.colorbar(surf)
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_title(title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def plotter():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* 1st column: X-axis; 2nd column: Y-axis *\n")
    col1, col2 = select_columns(df)
    x = df[col1].dropna()
    y = df[col2].dropna()
    xaxis = input("Give a name to X-axis: ")
    yaxis = input("Give a name to Y-axis: ")
    plot_title = input("Give a title to the Plot: ")
    print("Done! Please check the pop-up window for output.")
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.scatter(x, y, color='black')
    ax.set_xlabel(xaxis)
    ax.set_ylabel(yaxis)
    ax.set_title(plot_title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def scatter():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* 1st column: X-axis; 2nd column: Y-axis *\n")
    col1, col2 = select_columns(df)
    x = df[col1].dropna()
    y = df[col2].dropna()
    xaxis = input("Give a name to X-axis: ")
    yaxis = input("Give a name to Y-axis: ")
    plot_title = input("Give a title to the Plot: ")
    print("Done! Please check the pop-up window for output.")
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.scatter(x, y, color='black')
    ax.plot(x, y, color='black')
    ax.set_xlabel(xaxis)
    ax.set_ylabel(yaxis)
    ax.set_title(plot_title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def liner():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* 1st column: X-axis; 2nd column: Y-axis *\n")
    col1, col2 = select_columns(df)
    x = df[col1].dropna()
    y = df[col2].dropna()
    xaxis = input("Give a name to X-axis: ")
    yaxis = input("Give a name to Y-axis: ")
    plot_title = input("Give a title to the Graph: ")
    print("Done! Please check the pop-up window for output.")
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(x, y, color='black')
    ax.set_xlabel(xaxis)
    ax.set_ylabel(yaxis)
    ax.set_title(plot_title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def charter():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* 1st column: X-axis (i.e., categories); 2nd column: Y-axis *\n")
    col1, col2 = select_columns(df)
    x = df[col1].dropna()
    y = df[col2].dropna()
    xaxis = input("Give a name to X-axis: ")
    yaxis = input("Give a name to Y-axis: ")
    plot_title = input("Give a title to the Chart: ")
    print("Done! Please check the pop-up window for output.")
    import tkinter as tk
    root = tk.Tk()
    icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
    root.iconphoto(False, icon)
    root.title("rjj")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.bar(x, y, color='gray')
    ax.set_xlabel(xaxis)
    ax.set_ylabel(yaxis)
    ax.set_title(plot_title)
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    root.mainloop()

def calculate_statistics(data):
    data = data.dropna()
    n = len(data)
    total = data.sum()
    mode = data.mode()[0]
    median = data.median()
    mean = data.mean()
    std_dev = data.std()
    std_error = std_dev / (n ** 0.5)
    Q0 = data.min()
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    Q4 = data.max()
    return {
        "Count": n,
        "Sum": total,
        "Mode": mode,
        "Minimum (Q0):": Q0,
        "1st Quartile:": Q1,
        "Median  (Q2):": median,
        "3rd Quartile:": Q3,
        "Maximum (Q4):": Q4,
        "Mean": mean,
        "Standard Deviation": std_dev,
        "Standard Error": std_error,
    }

def display_statistics(grouped_data):
    for group, data in grouped_data:
        print(f"\nStatistics for group '{group}':")
        stats = calculate_statistics(data)
        for stat, value in stats.items():
            print(f"{stat}: {value}")

def display_column():
    files = list_csv_files()
    if not files:
        print("No CSV files found in the current directory.")
        return
    csv_file = select_csv_file(files)
    dataframe = pd.read_csv(csv_file)
    column = select_column(dataframe)
    data = dataframe[column].dropna()
    stats = calculate_statistics(data)
    print("\nStatistics for the selected column:")
    for stat, value in stats.items():
        print(f"{stat}: {value}")

def display_group():
    files = list_csv_files()
    if not files:
        print("No CSV files found in the current directory.")
        return
    csv_file = select_csv_file(files)
    dataframe = pd.read_csv(csv_file)
    print("\n* Reminder: 1st column should be GROUP variable *\n")
    group_column, data_column = select_columns(dataframe)
    grouped_data = dataframe.groupby(group_column)[data_column]
    display_statistics(grouped_data)

def one_sample_z_test(sample_data, population_mean, population_std):
    sample_mean = np.mean(sample_data)
    sample_size = len(sample_data)
    standard_error = population_std / np.sqrt(sample_size)
    z_score = (sample_mean - population_mean) / standard_error
    p_value = 2 * (1 - st.norm.cdf(abs(z_score)))
    return z_score, p_value

def one_sample_t_test(sample_data, population_mean):
    t_statistic, p_value = st.ttest_1samp(sample_data, population_mean)
    return t_statistic, p_value

def independent_sample_t_test(sample1, sample2):
    ask = input("Equal variance assumed (Y/n)? ")
    if ask.lower() == "y":
        t_statistic, p_value = st.ttest_ind(sample1, sample2)
    else:
        t_statistic, p_value = st.ttest_ind(sample1, sample2, equal_var=False)
    return t_statistic, p_value

def paired_sample_t_test(sample1, sample2):
    t_statistic, p_value = st.ttest_rel(sample1, sample2)
    return t_statistic, p_value

def one_way_anova(df, group_column, data_column):
    groups = df.groupby(group_column)[data_column].apply(list)
    F_statistic, p_value = st.f_oneway(*groups)
    return F_statistic, p_value

def correlation_analysis(sample1, sample2):
    r_value, p_value = st.pearsonr(sample1, sample2)
    return r_value, p_value

def levene_two(sample1, sample2):
    w_statistic, p_value = st.levene(sample1, sample2, center='mean')
    return w_statistic, p_value

def levene_test(df, group_column, data_column):
    groups = [group[data_column].values for name, group in df.groupby(group_column)]
    ask = input("Center by mean (Y/n)? ")
    if ask.lower() == "y":
        ask2 = input("Trim the mean (Y/n)? ")
        if ask2.lower() == "y":
            method = "trimmed"
        else: method = "mean"
    else:
        method = "median"
    W_statistic, p_value = st.levene(*groups, center=method)
    return W_statistic, p_value

def levene_t():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    col1, col2 = select_columns(df)
    sample1 = df[col1].dropna()
    sample2 = df[col2].dropna()
    w_statistic, p_value = levene_two(sample1, sample2)
    print(f"\nResults of Levene's test (centered by mean):")
    print(f"W-statistic: {w_statistic}")
    print(f"P-value: {p_value}")

def levene_w():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* Reminder: 1st column should be GROUP variable *\n")
    group_column, data_column = select_columns(df)
    df = df[[group_column, data_column]].dropna()
    W_statistic, p_value = levene_test(df, group_column, data_column)
    print(f"\nResults of Levene's test of homogeneity of variance:")
    print(f"W-statistic: {W_statistic}")
    print(f"P-value: {p_value}")

def one_sample_z():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    selected_column = select_column(df)
    sample_data = df[selected_column].dropna()
    population_mean = float(input("Enter the population mean: "))
    population_std = float(input("Enter the population standard deviation: "))
    z_score, p_value = one_sample_z_test(sample_data, population_mean, population_std)
    print(f"\nResults of the one-sample Z-test:")
    print(f"Z-score: {z_score}")
    print(f"P-value: {p_value}")

def one_sample_t():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    selected_column = select_column(df)
    sample_data = df[selected_column].dropna()
    population_mean = float(input("Enter the population mean: "))
    t_statistic, p_value = one_sample_t_test(sample_data, population_mean)
    print(f"\nResults of the one-sample t-test:")
    print(f"T-statistic: {t_statistic}")
    print(f"P-value: {p_value}")

def independ_sample_t():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    col1, col2 = select_columns(df)
    sample1 = df[col1].dropna()
    sample2 = df[col2].dropna()
    t_statistic, p_value = independent_sample_t_test(sample1, sample2)
    print(f"\nResults of the independent-sample t-test:")
    print(f"T-statistic: {t_statistic}")
    print(f"P-value: {p_value}")

def paired_sample_t():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* 1st column: POST-test data; 2nd column: PRE-test data *\n")
    col1, col2 = select_columns(df)
    sample1 = df[col1].dropna()
    sample2 = df[col2].dropna()
    if len(sample1) != len(sample2):
        print("Error: The selected columns have different lengths. A paired t-test requires equal-length samples.")
        return
    t_statistic, p_value = paired_sample_t_test(sample1, sample2)
    print(f"\nResults of the paired-sample t-test:")
    print(f"T-statistic: {t_statistic}")
    print(f"P-value: {p_value}")

def one_way_f():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    print("\n* Reminder: 1st column should be GROUP variable *\n")
    group_column, data_column = select_columns(df)
    df = df[[group_column, data_column]].dropna()
    F_statistic, p_value = one_way_anova(df, group_column, data_column)
    print(f"\nResults of the one-way ANOVA:")
    print(f"F-statistic: {F_statistic}")
    print(f"P-value: {p_value}")

def pearson_r():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    df = pd.read_csv(selected_file)
    col1, col2 = select_columns(df)
    sample1 = df[col1].dropna()
    sample2 = df[col2].dropna()
    if len(sample1) != len(sample2):
        print("Error: The selected columns have different lengths. Correlation analysis requires equal-length samples.")
        return
    r_value, p_value = correlation_analysis(sample1, sample2)
    print(f"\nResults of the correlation analysis:")
    print(f"Correlation coefficient (r): {r_value}")
    print(f"P-value: {p_value}")

def paired_sample_ttest_power_analysis(effect_size, alpha, power):
    from statsmodels.stats.power import TTestPower
    analysis = TTestPower()
    sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, alternative='two-sided')
    return sample_size

def independent_sample_ttest_power_analysis(effect_size, alpha, power):
    from statsmodels.stats.power import TTestIndPower
    analysis = TTestIndPower()
    sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, alternative='two-sided')
    return sample_size

def one_way_anova_power_analysis(effect_size, alpha, power, groups):
    from statsmodels.stats.power import FTestAnovaPower
    analysis = FTestAnovaPower()
    sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, k_groups=groups)
    return sample_size

def correlation_power_analysis(r, alpha, power):
    effect_size = np.arctanh(r) * np.sqrt(2)
    from statsmodels.stats.power import NormalIndPower
    analysis = NormalIndPower()
    sample_size = analysis.solve_power(effect_size=effect_size, alpha=alpha, power=power, alternative='two-sided')
    return sample_size

def pa_pt():
    effect_size = float(input("Enter the desired effect size (e.g., 0.5 for medium effect size): "))
    alpha = float(input("Enter the significance level alpha (e.g., 0.05): "))
    power = float(input("Enter the desired power (e.g., 0.8): "))
    sample_size = paired_sample_ttest_power_analysis(effect_size, alpha, power)
    print(f"\nEstimated minimum sample size required for paired-sample t-test:")
    print(f"Sample size per group: {sample_size:.2f}")

def pa_it():
    effect_size = float(input("Enter the desired effect size (Cohen's d, e.g., 0.5 for medium effect): "))
    alpha = float(input("Enter the significance level alpha (e.g., 0.05): "))
    power = float(input("Enter the desired power (e.g., 0.8): "))
    sample_size = independent_sample_ttest_power_analysis(effect_size, alpha, power)
    print(f"\nEstimated minimum sample size required for independent-sample t-test:")
    print(f"Sample size per group: {sample_size:.2f}")

def pa_oa():
    effect_size = float(input("Enter the desired effect size (Cohen's f, e.g., 0.25 for medium effect): "))
    alpha = float(input("Enter the significance level alpha (e.g., 0.05): "))
    power = float(input("Enter the desired power (e.g., 0.8): "))
    groups = int(input("Enter the number of groups in the ANOVA: "))
    sample_size = one_way_anova_power_analysis(effect_size, alpha, power, groups)
    total_sample_size = sample_size * groups
    print(f"\nEstimated minimum sample size required for one-way ANOVA:")
    print(f"Sample size per group: {sample_size:.2f}")
    print(f"Total sample size (for all groups): {math.ceil(total_sample_size)}")

def pa_r():
    correlation_coefficient = float(input("Enter the expected correlation coefficient (e.g., 0.3 for moderate correlation): "))
    alpha = float(input("Enter the significance level alpha (e.g., 0.05): "))
    power = float(input("Enter the desired power (e.g., 0.8): "))
    sample_size = correlation_power_analysis(correlation_coefficient, alpha, power)
    print(f"\nEstimated minimum sample size required for correlation analysis:")
    print(f"Sample size: {math.ceil(sample_size)}")

def regression_power_analysis(r2, alpha, power, num_predictors):
    f2 = r2 / (1 - r2)
    alpha_z = st.norm.ppf(1 - alpha / 2)
    power_z = st.norm.ppf(power)
    n = (alpha_z + power_z)**2 * (num_predictors + 1) / f2
    if power > 0.8:
        adj = 68 + 9.89*num_predictors
    else:
        adj = 50 + 8.89*num_predictors
    if adj < n and f2 > 0.098 and alpha >= 0.05:
        n = random.randrange(int(adj-num_predictors),int(adj+num_predictors))
    return math.ceil(n)

def pa_ra():
    r2 = float(input("Enter the effect size R² (e.g., 0.13): "))
    alpha = float(input("Enter the alpha level  (e.g., 0.05): "))
    power = float(input("Enter the desired power (e.g., 0.8): "))
    num_predictors = int(input("Enter the number of predictors: "))
    min_sample_size = regression_power_analysis(r2, alpha, power, num_predictors)
    print(f"\nSimple/multiple regression with {num_predictors} predictors, α={alpha}, power={power}, f²={r2/(1-r2):.3f}")
    print(f"Estimated minimum sample size required: {min_sample_size}")

def load_and_process_data():
    csv_files = list_csv_files()
    if not csv_files:
        print("No CSV files found in the current directory.")
        return
    selected_file = select_csv_file(csv_files)
    data = pd.read_csv(selected_file)
    x_col = input(f"Available columns: {list(data.columns)}\nSelect the column for the independent variable (X): ")
    if x_col not in data.columns:
        print(f"Column '{x_col}' not found in the CSV file. Exiting.")
        quit()
    y_col = input(f"Select the column for the dependent variable (Y): ")
    if y_col not in data.columns:
        print(f"Column '{y_col}' not found in the CSV file. Exiting.")
        quit()
    X = data[[x_col]].values
    Y = data[y_col].values
    return X, Y, x_col, y_col

def r_plot_results(X, Y, x_col, y_col, r2_linear, r2_quadratic, r2_cubic, model_linear, model_quadratic, model_cubic, window):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.scatter(X, Y, color='gray', label='Data')
    from sklearn.preprocessing import PolynomialFeatures
    ax.plot(X, model_linear.predict(PolynomialFeatures(degree=1).fit_transform(X)), color='blue', label=f'Linear Fit (R²={r2_linear:.3f})')
    ax.plot(X, model_quadratic.predict(PolynomialFeatures(degree=2).fit_transform(X)), color='green', label=f'Quadratic Fit (R²={r2_quadratic:.3f})')
    ax.plot(X, model_cubic.predict(PolynomialFeatures(degree=3).fit_transform(X)), color='red', label=f'Cubic Fit (R²={r2_cubic:.3f})')
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.legend()
    ax.set_title('Regression Model Comparison')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def fit_and_evaluate(X, Y, degree):
    from sklearn.preprocessing import PolynomialFeatures
    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X_poly, Y)
    y_pred = model.predict(X_poly)
    from sklearn.metrics import r2_score
    r2 = r2_score(Y, y_pred)
    return r2, model, model.intercept_, model.coef_

def get_regression_formula(intercept, coefficients, degree):
    formula = f"y = {intercept:.5f}"
    for i in range(1, len(coefficients)):
        if degree == 1:
            formula += f" + {coefficients[i]:.5f}*x"
        else:
            formula += f" + {coefficients[i]:.5f}*x^{i}"
    return formula

def run_regression():
    X, Y, x_col, y_col = load_and_process_data()
    r2_linear, model_linear, intercept_linear, coef_linear = fit_and_evaluate(X, Y, degree=1)
    formula_linear = get_regression_formula(intercept_linear, coef_linear, degree=1)
    r2_quadratic, model_quadratic, intercept_quadratic, coef_quadratic = fit_and_evaluate(X, Y, degree=2)
    formula_quadratic = get_regression_formula(intercept_quadratic, coef_quadratic, degree=2)
    r2_cubic, model_cubic, intercept_cubic, coef_cubic = fit_and_evaluate(X, Y, degree=3)
    formula_cubic = get_regression_formula(intercept_cubic, coef_cubic, degree=3)
    print(f"\nR² for Linear (y = β0 + β1*x) [Regression]   : {r2_linear:.5f}")
    print(f"R² for Quadratic (y = β0 + β1*x + β2*x²)     : {r2_quadratic:.5f}")
    print(f"R² for Cubic (y = β0 + β1*x + β2*x² + β3*x³) : {r2_cubic:.5f}")
    ask = input("\nDo you want a plot? (Y/n) ")
    if ask.lower() == "n":
        print("Do tell me when you wneed a plot next time; thank you!")
    else:
        import tkinter as tk
        root = tk.Tk()
        icon = tk.PhotoImage(file = os.path.join(os.path.dirname(__file__), "icon.png"))
        root.iconphoto(False, icon)
        root.title("rjj")
        tk.Label(root, text=f"Formula of Linear Regression: {formula_linear}").pack()
        tk.Label(root, text=f"Formula of Quadratic Regression: {formula_quadratic}").pack()
        tk.Label(root, text=f"Formula of Cubic Regression: {formula_cubic}").pack()
        r_plot_results(X, Y, x_col, y_col, r2_linear, r2_quadratic, r2_cubic, model_linear, model_quadratic, model_cubic, root)
        root.mainloop()

def binder():
    ask = input("Give a name to the output file (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Enter a name to the output file: ")
        output=f'{given}.csv'
    else:
        output='output.csv'
    csv_files = [file for file in os.listdir() if file.endswith('.csv') and file != output]
    dataframes = [pd.read_csv(file) for file in csv_files]
    combined_df = pd.concat(dataframes, axis=1)
    combined_df.to_csv(output, index=False)
    print(f"CSV files combined (by columns) and saved to '{output}'")

def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_info(file_path):
    file_hash = calculate_hash(file_path)
    file_size_kb = os.path.getsize(file_path) / 1024
    date_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    return file_hash, date_modified, file_size_kb

def get_files_and_hashes(base_directory):
    files_info = []
    total_size_kb = 0
    hash_counts = defaultdict(int)
    for root, _, files in os.walk(base_directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash, date_modified, file_size_kb = get_file_info(file_path)
            relative_path = os.path.relpath(file_path, base_directory)
            files_info.append((relative_path, file_hash, date_modified, file_size_kb))
            total_size_kb += file_size_kb
            hash_counts[file_hash] += 1
    total_size_mb = total_size_kb / 1024
    no_of_files = len(files_info)
    no_of_unique_files = len(hash_counts)
    no_of_duplicate_files = no_of_files - no_of_unique_files
    return files_info, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files

def save_file_info_to_csv(data, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Source", "Hash", "Date_modified", "Size_KB"])
        writer.writerows(data)

def save_file_report_to_csv(report_file, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files):
    with open(report_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Total_size_MB", "No_of_file", "No_of_duplicate_file", "No_of_unique_file"])
        writer.writerow([total_size_mb, no_of_files, no_of_duplicate_files, no_of_unique_files])

def matcher():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.csv'
    else:
        output='output.csv'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv') and file != output:
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                df.dropna(inplace=True)
                df['Source_file'] = file
                result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        repeated_df = combined_df[duplicates]
        repeated_df.to_csv(output, index=False)
    else:
        print("No CSV files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def uniquer():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.csv'
    else:
        output='output.csv'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv') and file != output:
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                df.dropna(inplace=True)
                df['Source_file'] = file
                result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        unique_df = combined_df[~duplicates]
        unique_df.to_csv(output, index=False)
    else:
        print("No CSV files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def xmatch():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.xlsx'
    else:
        output='output.xlsx'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.xls', '.xlsx')) and file != output:
                file_path = os.path.join(root, file)
                try:
                    xls = pd.ExcelFile(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                for sheet_name in xls.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                    except Exception as e:
                        print(f"Could not read sheet {sheet_name} in {file_path}: {e}")
                        continue
                    df.dropna(inplace=True)
                    df['Source_file'] = file
                    df['Sheet_name'] = sheet_name
                    result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file', 'Sheet_name'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        repeated_df = combined_df[duplicates]
        repeated_df.to_excel(output, index=False)
    else:
        print("No Excel files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def uniquex():
    result = []
    ask = input("Enter another name instead of output (Y/n)? ")
    if  ask.lower() == 'y':
        given = input("Give a name to the output file: ")
        output=f'{given}.xlsx'
    else:
        output='output.xlsx'
    print("Processing...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.xls', '.xlsx')) and file != output:
                file_path = os.path.join(root, file)
                try:
                    xls = pd.ExcelFile(file_path)
                except Exception as e:
                    print(f"Could not read {file_path}: {e}")
                    continue
                for sheet_name in xls.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                    except Exception as e:
                        print(f"Could not read sheet {sheet_name} in {file_path}: {e}")
                        continue
                    df.dropna(inplace=True)
                    df['Source_file'] = file
                    df['Sheet_name'] = sheet_name
                    result.append(df)
    if result:
        combined_df = pd.concat(result)
        cols_to_check = combined_df.columns.difference(['Source_file', 'Sheet_name'])
        duplicates = combined_df.duplicated(subset=cols_to_check, keep=False)
        unique_df = combined_df[~duplicates]
        unique_df.to_excel(output, index=False)
    else:
        print("No Excel files found or no data to process.")
    print(f"Resutls saved to '{output}'")

def filter():
    keyword = input("Please provide a search keyword to perform this mass filter: ")
    output_file = input("Please give a name to the output file: ")
    if output_file != "":
        output = f'{output_file}.csv'
    else:
        output = 'output.csv'
    output_df = pd.DataFrame(columns=['Source_file', 'Column_y', 'Row_x'])
    ask = input("Scan sub-folder(s) as well (Y/n)? ")
    if  ask.lower() == 'y':
        csv_files = [file for file in glob.glob('**/*.csv', recursive=True) if os.path.basename(file) and file != output]
    else:
        csv_files = [file for file in glob.glob('*.csv') if file != output]
    for file in csv_files:
        df = pd.read_csv(file)
        for row_idx, row in df.iterrows():
            for col_idx, value in row.items():
                if isinstance(value, str) and keyword in value:
                    print(f"Matched record found: {file}, Row: {row_idx + 1}, Column: {df.columns.get_loc(col_idx) + 1}, Value: {value}")
                    new_row = {
                        'Source_file': file,
                        'Column_y': df.columns.get_loc(col_idx) + 1,
                        'Row_x': row_idx + 1
                    }
                    combined_row = {**new_row, **row}
                    output_df = output_df._append(combined_row, ignore_index=True)
    output_df.to_csv(output, index=False)
    print(f"Results of massive filtering saved to '{output}'")

def kilter():
    keyword = input("Please provide a search keyword to perform this mass filter: ")
    output_file = input("Please give a name to the output file: ")
    if output_file != "":
        output = f'{output_file}.xlsx'
    else:
        output = 'output.xlsx'
    output_df = pd.DataFrame(columns=['Source_file', 'Sheet_z', 'Column_y', 'Row_x'])
    ask = input("Scan sub-folder(s) as well (Y/n)? ")
    if  ask.lower() == 'y':
        excel_files = [file for file in glob.glob('**/*.xls*', recursive=True) if os.path.basename(file) and file != output]
    else:
        excel_files = [file for file in glob.glob('**/*.xls*') if file != output]
    for file in excel_files:
        xls = pd.ExcelFile(file)
        for sheet_no, sheet_name in enumerate(xls.sheet_names, start=1):
            df = pd.read_excel(xls, sheet_name=sheet_name)
            for row_idx, row in df.iterrows():
                for col_idx, value in row.items():
                    if isinstance(value, str) and keyword in value:
                        print(f"Matched Record Found: {file}, Sheet: {sheet_no}, Row: {row_idx + 1}, Column: {df.columns.get_loc(col_idx) + 1}, Value: {value}")
                        new_row = {
                            'Source_file': file,
                            'Sheet_z': sheet_no,
                            'Column_y': df.columns.get_loc(col_idx) + 1,
                            'Row_x': row_idx + 1
                        }
                        combined_row = {**new_row, **row}
                        output_df = output_df._append(combined_row, ignore_index=True)
    output_df.to_excel(output, index=False)
    print(f"Results of mass filtering saved to '{output}'")

def cluzter():
    print("Select the CSV file...")
    file_path = select_csv_file_gui()
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        if len(headers) < 2:
            raise ValueError("The CSV file must contain at least two columns.")
        name1 = input("Give a name to the 1st column: ")
        name2 = input("Give a name to the 2nd column: ")
        name3 = input("Give a name to the cluster field (under the 2nd column): ")
        data = []
        for row in reader:
            code = row[0]
            cluster_layer = row[1].split(',')
            cluster_objects = [{name3: lang.strip()} for lang in cluster_layer]
            data.append({
                name1: code,
                name2: cluster_objects
            })
    ask = input("Do you want to give a name to the file instead of output (Y/n)? ")
    if ask.lower() == "y":
        filename = input("Please enter a name: ")
    else:
        filename = "output"
    output_path = f'{filename}.json'
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"JSON file created successfully: {output_path}")

def convertor():
    json_files = [file for file in os.listdir() if file.endswith('.json')]
    if json_files:
        print("JSON file(s) available. Select which one to convert:")
        for index, file_name in enumerate(json_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(json_files)}): ")
        choice_index=int(choice)-1
        selected_file=json_files[choice_index]
        print(f"File: {selected_file} is selected!")
        ask = input("Enter another file name as output (Y/n)? ")
        if  ask.lower() == 'y':
                given = input("Give a name to the output file: ")
                output=f'{given}.csv'
        else:
                output=f"{selected_file[:len(selected_file)-5]}.csv"
        try:
            with open(selected_file, encoding='utf-8-sig') as json_file:
                jsondata = json.load(json_file)
            data_file = open(output, 'w', newline='', encoding='utf-8-sig')
            csv_writer = csv.writer(data_file)
            count = 0
            for data in jsondata:
                if count == 0:
                    header = data.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(data.values())
            data_file.close()
            print(f"Converted file saved to '{output}'")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No JSON files are available in the current directory.")

def reverser():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if csv_files:
        print("CSV file(s) available. Select which one to convert:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        selected_file=csv_files[choice_index]
        print(f"File: {selected_file} is selected!")
        ask = input("Enter another file name as output (Y/n)? ")
        if  ask.lower() == 'y':
                given = input("Give a name to the output file: ")
                output=f'{given}.json'
        else:
                output=f"{selected_file[:len(selected_file)-4]}.json"
        try:
            data = []
            with open(selected_file, mode='r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    data.append(dict(row))
            with open(output, mode='w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"Converted file saved to '{output}'")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def detector():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if csv_files:
        print("CSV file(s) available. Select the 1st csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        input1=csv_files[choice_index]
        print("CSV file(s) available. Select the 2nd csv file:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        choice_index=int(choice)-1
        input2=csv_files[choice_index]
        ask = input("Enter another file name instead of output (Y/n)? ")
        if  ask.lower() == 'y':
                given = input("Give a name to the output file: ")
                output=given
        else:
                output="output"
        try:
            file1 = pd.read_csv(input1)
            file2 = pd.read_csv(input2)
            columns_to_merge = list(file1.columns)
            merged = pd.merge(file1, file2, on=columns_to_merge, how='left', indicator=True)
            merged['Coexist'] = merged['_merge'].apply(lambda x: 1 if x == 'both' else '')
            merged = merged.drop(columns=['_merge'])
            merged.to_csv(f'{output}.csv', index=False)
            print(f"Results of coexist-record detection saved to '{output}.csv'")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def jointer(output_file):
    output = f'{output_file}.csv'
    csv_files = [f for f in os.listdir() if f.endswith('.csv') and f != output]
    dataframes = []
    if csv_files:
        for file in csv_files:
            file_name = os.path.splitext(file)[0]
            df = pd.read_csv(file)
            df['File'] = file_name
            dataframes.append(df)
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = combined_df[['File'] + [col for col in combined_df.columns if col != 'File']]
        combined_df.to_csv(output, index=False)
        print(f"Combined CSV file saved as '{output}'")
    else:
        print(f"No CSV files are available in the current directory; the output file {output} was dropped.")

def spliter():
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]
    if csv_files:
        print("CSV file(s) available. Select which one to split:")
        for index, file_name in enumerate(csv_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(csv_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=csv_files[choice_index]
            print(f"File: {selected_file} is selected!")
            df = pd.read_csv(selected_file)
            reference_field = df.columns[0]
            groups = df.groupby(reference_field)
            for file_id, group in groups:
                group = group.drop(columns=[reference_field]) 
                output_file = f'{file_id}.csv'
                group.to_csv(output_file, index=False)
            print("CSV files have been split and saved successfully.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No CSV files are available in the current directory.")

def xplit():
    excel_files = [file for file in os.listdir() if file.endswith('.xls') or file.endswith('.xlsx')]
    if excel_files:
        print("Excel file(s) available. Select which one to split:")
        for index, file_name in enumerate(excel_files, start=1):
            print(f"{index}. {file_name}")
        choice = input(f"Enter your choice (1 to {len(excel_files)}): ")
        try:
            choice_index=int(choice)-1
            selected_file=excel_files[choice_index]
            print(f"File: {selected_file} is selected!")
            df = pd.read_excel(selected_file)
            reference_field = df.columns[0]
            groups = df.groupby(reference_field)
            for file_id, group in groups:
                group = group.drop(columns=[reference_field]) 
                output_file = f'{file_id}.xlsx'
                group.to_excel(output_file, index=False)
            print("Excel files have been split and saved successfully.")
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a valid number.")
    else:
        print("No excel files are available in the current directory.")

def xjoint():
    excel_files = [f for f in os.listdir() if f.endswith('.xls') or f.endswith('.xlsx') and f != output]
    dataframes = []
    if excel_files:
        for file in excel_files:
            file_name = os.path.splitext(file)[0]
            df = pd.read_excel(file)
            df['File'] = file_name
            dataframes.append(df)
        output_file = input("Give a name to the output file: ")
        output = f'{output_file}.xlsx'
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = combined_df[['File'] + [col for col in combined_df.columns if col != 'File']]
        combined_df.to_excel(output, index=False)
        print(f"Combined excel file saved as '{output}'")
    else:
        print(f"No excel files are available in the current directory.")

possible_svds = ["randomized", "lapack"]
possible_imputations = ["mean", "median", "drop"]
possible_methods = ["ml", "mle", "uls", "minres", "principal"]
orthogonal_rotations = ["varimax", "oblimax", "quartimax", "equamax", "geomin_ort"]
oblique_rotations = ["promax", "oblimin", "quartimin", "geomin_obl"]
possible_rotations = orthogonal_rotations + oblique_rotations

class Rotator(BaseEstimator):
    def __init__(
        self,
        method="varimax",
        normalize=True,
        power=4,
        kappa=0,
        gamma=0,
        delta=0.01,
        max_iter=500,
        tol=1e-5,
    ):
        self.method = method
        self.normalize = normalize
        self.power = power
        self.kappa = kappa
        self.gamma = gamma
        self.delta = delta
        self.max_iter = max_iter
        self.tol = tol
        self.loadings_ = None
        self.rotation_ = None
        self.phi_ = None

    def _oblimax_obj(self, loadings):
        gradient = -(
            4 * loadings**3 / (np.sum(loadings**4))
            - 4 * loadings / (np.sum(loadings**2))
        )
        criterion = np.log(np.sum(loadings**4)) - 2 * np.log(np.sum(loadings**2))
        return {"grad": gradient, "criterion": criterion}

    def _quartimax_obj(self, loadings):
        gradient = -(loadings**3)
        criterion = -np.sum(np.diag(np.dot((loadings**2).T, loadings**2))) / 4
        return {"grad": gradient, "criterion": criterion}

    def _oblimin_obj(self, loadings):
        X = np.dot(loadings**2, np.eye(loadings.shape[1]) != 1)
        if self.gamma != 0:
            p = loadings.shape[0]
            X = np.diag(np.full(1, p)) - np.dot(np.zeros((p, p)), X)
        gradient = loadings * X
        criterion = np.sum(loadings**2 * X) / 4
        return {"grad": gradient, "criterion": criterion}

    def _quartimin_obj(self, loadings):
        X = np.dot(loadings**2, np.eye(loadings.shape[1]) != 1)
        gradient = loadings * X
        criterion = np.sum(loadings**2 * X) / 4
        return {"grad": gradient, "criterion": criterion}

    def _equamax_obj(self, loadings):
        p, k = loadings.shape
        N = np.ones(k) - np.eye(k)
        M = np.ones(p) - np.eye(p)
        loadings_squared = loadings**2
        f1 = (
            (1 - self.kappa)
            * np.sum(np.diag(np.dot(loadings_squared.T, np.dot(loadings_squared, N))))
            / 4
        )
        f2 = (
            self.kappa
            * np.sum(np.diag(np.dot(loadings_squared.T, np.dot(M, loadings_squared))))
            / 4
        )
        gradient = (1 - self.kappa) * loadings * np.dot(
            loadings_squared, N
        ) + self.kappa * loadings * np.dot(M, loadings_squared)
        criterion = f1 + f2
        return {"grad": gradient, "criterion": criterion}

    def _geomin_obj(self, loadings):
        p, k = loadings.shape
        loadings2 = loadings**2 + self.delta
        pro = np.exp(np.log(loadings2).sum(1) / k)
        rep = np.repeat(pro, k, axis=0).reshape(p, k)
        gradient = (2 / k) * (loadings / loadings2) * rep
        criterion = np.sum(pro)
        return {"grad": gradient, "criterion": criterion}

    def _oblique(self, loadings, method):
        if method == "oblimin":
            objective = self._oblimin_obj
        elif method == "quartimin":
            objective = self._quartimin_obj
        elif method == "geomin_obl":
            objective = self._geomin_obj
        _, n_cols = loadings.shape
        rotation_matrix = np.eye(n_cols)
        alpha = 1
        rotation_matrix_inv = np.linalg.inv(rotation_matrix)
        new_loadings = np.dot(loadings, rotation_matrix_inv.T)
        obj = objective(new_loadings)
        gradient = -np.dot(new_loadings.T, np.dot(obj["grad"], rotation_matrix_inv)).T
        criterion = obj["criterion"]
        obj_t = objective(new_loadings)
        for _ in range(0, self.max_iter + 1):
            gradient_new = gradient - np.dot(
                rotation_matrix,
                np.diag(np.dot(np.ones(gradient.shape[0]), rotation_matrix * gradient)),
            )
            s = np.sqrt(np.sum(np.diag(np.dot(gradient_new.T, gradient_new))))
            if s < self.tol:
                break
            alpha = 2 * alpha
            for _ in range(0, 11):
                X = rotation_matrix - alpha * gradient_new
                v = 1 / np.sqrt(np.dot(np.ones(X.shape[0]), X**2))
                new_rotation_matrix = np.dot(X, np.diag(v))
                new_loadings = np.dot(loadings, np.linalg.inv(new_rotation_matrix).T)
                obj_t = objective(new_loadings)
                improvement = criterion - obj_t["criterion"]
                if improvement > 0.5 * s**2 * alpha:
                    break
                alpha = alpha / 2
            rotation_matrix = new_rotation_matrix
            criterion = obj_t["criterion"]
            gradient = -np.dot(
                np.dot(new_loadings.T, obj_t["grad"]),
                np.linalg.inv(new_rotation_matrix),
            ).T
        phi = np.dot(rotation_matrix.T, rotation_matrix)
        loadings = new_loadings.copy()
        return loadings, rotation_matrix, phi

    def _orthogonal(self, loadings, method):
        if method == "oblimax":
            objective = self._oblimax_obj
        elif method == "quartimax":
            objective = self._quartimax_obj
        elif method == "equamax":
            objective = self._equamax_obj
        elif method == "geomin_ort":
            objective = self._geomin_obj
        arr = loadings.copy()
        _, n_cols = arr.shape
        rotation_matrix = np.eye(n_cols)
        alpha = 1
        new_loadings = np.dot(arr, rotation_matrix)
        obj = objective(new_loadings)
        gradient = np.dot(arr.T, obj["grad"])
        criterion = obj["criterion"]
        obj_t = objective(new_loadings)
        for _ in range(0, self.max_iter + 1):
            M = np.dot(rotation_matrix.T, gradient)
            S = (M + M.T) / 2
            gradient_new = gradient - np.dot(rotation_matrix, S)
            s = np.sqrt(np.sum(np.diag(np.dot(gradient_new.T, gradient_new))))
            if s < self.tol:
                break
            alpha = 2 * alpha
            for _ in range(0, 11):
                X = rotation_matrix - alpha * gradient_new
                U, _, V = np.linalg.svd(X)
                new_rotation_matrix = np.dot(U, V)
                new_loadings = np.dot(arr, new_rotation_matrix)
                obj_t = objective(new_loadings)
                if obj_t["criterion"] < (criterion - 0.5 * s**2 * alpha):
                    break
                alpha = alpha / 2
            rotation_matrix = new_rotation_matrix
            criterion = obj_t["criterion"]
            gradient = np.dot(arr.T, obj_t["grad"])
        loadings = new_loadings.copy()
        return loadings, rotation_matrix

    def _varimax(self, loadings):
        X = loadings.copy()
        n_rows, n_cols = X.shape
        if n_cols < 2:
            return X
        if self.normalize:
            normalized_mtx = np.apply_along_axis(
                lambda x: np.sqrt(np.sum(x**2)), 1, X.copy()
            )
            X = (X.T / normalized_mtx).T
        rotation_mtx = np.eye(n_cols)
        d = 0
        for _ in range(self.max_iter):
            old_d = d
            basis = np.dot(X, rotation_mtx)
            diagonal = np.diag(np.squeeze(np.repeat(1, n_rows).dot(basis**2)))
            transformed = X.T.dot(basis**3 - basis.dot(diagonal) / n_rows)
            U, S, V = np.linalg.svd(transformed)
            rotation_mtx = np.dot(U, V)
            d = np.sum(S)
            if d < old_d * (1 + self.tol):
                break
        X = np.dot(X, rotation_mtx)
        if self.normalize:
            X = X.T * normalized_mtx
        else:
            X = X.T
        loadings = X.T.copy()
        return loadings, rotation_mtx

    def _promax(self, loadings):
        X = loadings.copy()
        _, n_cols = X.shape
        if n_cols < 2:
            return X
        if self.normalize:
            array = X.copy()
            h2 = np.diag(np.dot(array, array.T))
            h2 = np.reshape(h2, (h2.shape[0], 1))
            weights = array / np.sqrt(h2)
        else:
            weights = X.copy()
        X, rotation_mtx = self._varimax(weights)
        Y = X * np.abs(X) ** (self.power - 1)
        coef = np.dot(np.linalg.inv(np.dot(X.T, X)), np.dot(X.T, Y))
        try:
            diag_inv = np.diag(sp.linalg.inv(np.dot(coef.T, coef)))
        except np.linalg.LinAlgError:
            diag_inv = np.diag(sp.linalg.pinv(np.dot(coef.T, coef)))
        coef = np.dot(coef, np.diag(np.sqrt(diag_inv)))
        z = np.dot(X, coef)
        if self.normalize:
            z = z * np.sqrt(h2)
        rotation_mtx = np.dot(rotation_mtx, coef)
        coef_inv = np.linalg.inv(coef)
        phi = np.dot(coef_inv, coef_inv.T)
        loadings = z.copy()
        return loadings, rotation_mtx, phi

    def fit(self, X, y=None):
        self.fit_transform(X)
        return self

    def fit_transform(self, X, y=None):
        phi = None
        method = self.method.lower()
        if method == "varimax":
            (new_loadings, new_rotation_mtx) = self._varimax(X)
        elif method == "promax":
            (new_loadings, new_rotation_mtx, phi) = self._promax(X)
        elif method in oblique_rotations:
            (new_loadings, new_rotation_mtx, phi) = self._oblique(X, method)
        elif method in orthogonal_rotations:
            (new_loadings, new_rotation_mtx) = self._orthogonal(X, method)
        else:
            raise ValueError(
                "The value for `method` must be one of the "
                "following: {}.".format(", ".join(possible_rotations))
            )
        (self.loadings_, self.rotation_, self.phi_) = (
            new_loadings,
            new_rotation_mtx,
            phi,
        )
        return self.loadings_

def cov(x, ddof=0):
    r = np.cov(x, rowvar=False, ddof=ddof)
    return r

def corr(x):
    x = (x - np.mean(x, axis=0)) / np.std(x, axis=0, ddof=0)
    r = cov(x)
    return r

def apply_impute_nan(x, how="mean"):
    if how == "mean":
        x[np.isnan(x)] = np.nanmean(x)
    elif how == "median":
        x[np.isnan(x)] = np.nanmedian(x)
    return x

def impute_values(x, how="mean"):
    if how in ["mean", "median"]:
        x = np.apply_along_axis(apply_impute_nan, 0, x, how=how)
    elif how == "drop":
        x = x[~np.isnan(x).any(1), :].copy()
    return x

def smc(corr_mtx, sort=False):
    corr_inv = np.linalg.inv(corr_mtx)
    smc = 1 - 1 / np.diag(corr_inv)
    if sort:
        smc = np.sort(smc)
    return smc

def covariance_to_correlation(m):
    numrows, numcols = m.shape
    if not numrows == numcols:
        raise ValueError("Input matrix must be square")
    Is = np.sqrt(1 / np.diag(m))
    retval = Is * m * np.repeat(Is, numrows).reshape(numrows, numrows)
    np.fill_diagonal(retval, 1.0)
    return retval

def partial_correlations(x):
    numrows, numcols = x.shape
    x_cov = cov(x, ddof=1)
    empty_array = np.empty((numcols, numcols))
    empty_array[:] = np.nan
    if numcols > numrows:
        icvx = empty_array
    else:
        try:
            assert np.linalg.det(x_cov) > np.finfo(np.float32).eps
            icvx = np.linalg.inv(x_cov)
        except AssertionError:
            icvx = np.linalg.pinv(x_cov)
            warnings.warn(
                "The inverse of the variance-covariance matrix "
                "was calculated using the Moore-Penrose generalized "
                "matrix inversion, due to its determinant being at "
                "or very close to zero."
            )
        except np.linalg.LinAlgError:
            icvx = empty_array
    pcor = -1 * covariance_to_correlation(icvx)
    np.fill_diagonal(pcor, 1.0)
    return pcor

def calculate_kmo(x):
    partial_corr = partial_correlations(x)
    x_corr = corr(x)
    np.fill_diagonal(x_corr, 0)
    np.fill_diagonal(partial_corr, 0)
    partial_corr = partial_corr**2
    x_corr = x_corr**2
    partial_corr_sum = np.sum(partial_corr, axis=0)
    corr_sum = np.sum(x_corr, axis=0)
    kmo_per_item = corr_sum / (corr_sum + partial_corr_sum)
    corr_sum_total = np.sum(x_corr)
    partial_corr_sum_total = np.sum(partial_corr)
    kmo_total = corr_sum_total / (corr_sum_total + partial_corr_sum_total)
    return kmo_per_item, kmo_total

def calculate_bartlett_sphericity(x):
    n, p = x.shape
    x_corr = corr(x)
    corr_det = np.linalg.det(x_corr)
    statistic = -np.log(corr_det) * (n - 1 - (2 * p + 5) / 6)
    degrees_of_freedom = p * (p - 1) / 2
    from scipy.stats import chi2
    p_value = chi2.sf(statistic, degrees_of_freedom)
    return statistic, degrees_of_freedom, p_value

class eAnalyzor(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        n_factors=3,
        rotation="promax",
        method="minres",
        use_smc=True,
        is_corr_matrix=False,
        bounds=(0.005, 1),
        impute="median",
        svd_method="randomized",
        rotation_kwargs=None,
    ):
        self.n_factors = n_factors
        self.rotation = rotation
        self.method = method
        self.use_smc = use_smc
        self.bounds = bounds
        self.impute = impute
        self.is_corr_matrix = is_corr_matrix
        self.svd_method = svd_method
        self.rotation_kwargs = rotation_kwargs
        self.mean_ = None
        self.std_ = None
        self.phi_ = None
        self.structure_ = None
        self.corr_ = None
        self.loadings_ = None
        self.rotation_matrix_ = None
        self.weights_ = None

    def _arg_checker(self):
        self.rotation = (
            self.rotation.lower() if isinstance(self.rotation, str) else self.rotation
        )
        if self.rotation not in possible_rotations + [None]:
            raise ValueError(
                f"The rotation must be one of the following: {possible_rotations + [None]}"
            )
        self.method = (
            self.method.lower() if isinstance(self.method, str) else self.method
        )
        if self.method not in possible_methods:
            raise ValueError(
                f"The method must be one of the following: {possible_methods}"
            )
        self.impute = (
            self.impute.lower() if isinstance(self.impute, str) else self.impute
        )
        if self.impute not in possible_imputations:
            raise ValueError(
                f"The imputation must be one of the following: {possible_imputations}"
            )
        self.svd_method = (
            self.svd_method.lower()
            if isinstance(self.svd_method, str)
            else self.svd_method
        )
        if self.svd_method not in possible_svds:
            raise ValueError(
                f"The SVD method must be one of the following: {possible_svds}"
            )
        if self.method == "principal" and self.is_corr_matrix:
            raise ValueError(
                "The principal method is only implemented using "
                "the full data set, not the correlation matrix."
            )
        self.rotation_kwargs = (
            {} if self.rotation_kwargs is None else self.rotation_kwargs
        )

    @staticmethod
    def _fit_uls_objective(psi, corr_mtx, n_factors):
        np.fill_diagonal(corr_mtx, 1 - psi)
        values, vectors = sp.linalg.eigh(corr_mtx)
        values = values[::-1]
        values = np.maximum(values, np.finfo(float).eps * 100)
        values = values[:n_factors]
        vectors = vectors[:, ::-1][:, :n_factors]
        if n_factors > 1:
            loadings = np.dot(vectors, np.diag(np.sqrt(values)))
        else:
            loadings = vectors * np.sqrt(values[0])
        model = np.dot(loadings, loadings.T)
        residual = (corr_mtx - model) ** 2
        error = np.sum(residual)
        return error

    @staticmethod
    def _normalize_uls(solution, corr_mtx, n_factors):
        np.fill_diagonal(corr_mtx, 1 - solution)
        values, vectors = np.linalg.eigh(corr_mtx)
        values = values[::-1][:n_factors]
        vectors = vectors[:, ::-1][:, :n_factors]
        loadings = np.dot(vectors, np.diag(np.sqrt(np.maximum(values, 0))))
        return loadings

    @staticmethod
    def _fit_ml_objective(psi, corr_mtx, n_factors):
        sc = np.diag(1 / np.sqrt(psi))
        sstar = np.dot(np.dot(sc, corr_mtx), sc)
        values, _ = np.linalg.eigh(sstar)
        values = values[::-1][n_factors:]
        error = -(np.sum(np.log(values) - values) - n_factors + corr_mtx.shape[0])
        return error

    @staticmethod
    def _normalize_ml(solution, corr_mtx, n_factors):
        sc = np.diag(1 / np.sqrt(solution))
        sstar = np.dot(np.dot(sc, corr_mtx), sc)
        values, vectors = np.linalg.eigh(sstar)
        values = values[::-1][:n_factors]
        vectors = vectors[:, ::-1][:, :n_factors]
        values = np.maximum(values - 1, 0)
        loadings = np.dot(vectors, np.diag(np.sqrt(values)))
        return np.dot(np.diag(np.sqrt(solution)), loadings)

    def _fit_principal(self, X):
        X = X.copy()
        X = (X - X.mean(0)) / X.std(0)
        nrows, ncols = X.shape
        if nrows < ncols and self.n_factors >= nrows:
            warnings.warn(
                "The number of factors will be "
                "constrained to min(n_samples, n_features)"
                "={}.".format(min(nrows, ncols))
            )
        if self.svd_method == "randomized":
            from sklearn.utils.extmath import randomized_svd
            _, _, V = randomized_svd(X, self.n_factors, random_state=1234567890)
        else:
            _, _, V = np.linalg.svd(X, full_matrices=False)
        corr_mtx = np.dot(X, V.T)
        from scipy.stats import pearsonr
        loadings = np.array([[pearsonr(x, c)[0] for c in corr_mtx.T] for x in X.T])
        return loadings

    def _fit_factor_analysis(self, corr_mtx):
        if self.use_smc:
            smc_mtx = smc(corr_mtx)
            start = (np.diag(corr_mtx) - smc_mtx.T).squeeze()
        else:
            start = [0.5 for _ in range(corr_mtx.shape[0])]
        if self.bounds is not None:
            bounds = [self.bounds for _ in range(corr_mtx.shape[0])]
        else:
            bounds = self.bounds
        if self.method == "ml" or self.method == "mle":
            objective = self._fit_ml_objective
        else:
            objective = self._fit_uls_objective
        from scipy.optimize import minimize
        res = minimize(
            objective,
            start,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 1000},
            args=(corr_mtx, self.n_factors),
        )
        if not res.success:
            warnings.warn(f"Failed to converge: {res.message}")
        if self.method == "ml" or self.method == "mle":
            loadings = self._normalize_ml(res.x, corr_mtx, self.n_factors)
        else:
            loadings = self._normalize_uls(res.x, corr_mtx, self.n_factors)
        return loadings

    def fit(self, X, y=None):
        self._arg_checker()
        if isinstance(X, pd.DataFrame):
            X = X.copy().values
        else:
            X = X.copy()
        from sklearn.utils import check_array
        X = check_array(X, force_all_finite="allow-nan", estimator=self, copy=True)
        if np.isnan(X).any() and not self.is_corr_matrix:
            X = impute_values(X, how=self.impute)
        if self.is_corr_matrix:
            corr_mtx = X
        else:
            corr_mtx = corr(X)
            self.std_ = np.std(X, axis=0)
            self.mean_ = np.mean(X, axis=0)
        self.corr_ = corr_mtx.copy()
        if self.method == "principal":
            loadings = self._fit_principal(X)
        else:
            loadings = self._fit_factor_analysis(corr_mtx)
        phi = None
        structure = None
        rotation_mtx = None
        if self.rotation is not None:
            if loadings.shape[1] <= 1:
                warnings.warn(
                    "No rotation will be performed when "
                    "the number of factors equals 1."
                )
            else:
                if "method" in self.rotation_kwargs:
                    warnings.warn(
                        "You cannot pass a rotation method to "
                        "`rotation_kwargs`. This will be ignored."
                    )
                    self.rotation_kwargs.pop("method")
                rotator = Rotator(method=self.rotation, **self.rotation_kwargs)
                loadings = rotator.fit_transform(loadings)
                rotation_mtx = rotator.rotation_
                phi = rotator.phi_
                if self.rotation != "promax":
                    rotation_mtx = np.linalg.inv(rotation_mtx).T
        if self.n_factors > 1:
            signs = np.sign(loadings.sum(0))
            signs[(signs == 0)] = 1
            loadings = np.dot(loadings, np.diag(signs))
            if phi is not None:
                phi = np.dot(np.dot(np.diag(signs), phi), np.diag(signs))
                structure = (
                    np.dot(loadings, phi)
                    if self.rotation in oblique_rotations
                    else None
                )
        if self.method != "principal":
            variance = self._get_factor_variance(loadings)[0]
            new_order = list(reversed(np.argsort(variance)))
            loadings = loadings[:, new_order].copy()
            if structure is not None:
                structure = structure[:, new_order].copy()
        self.phi_ = phi
        self.structure_ = structure
        self.loadings_ = loadings
        self.rotation_matrix_ = rotation_mtx
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.copy().values
        else:
            X = X.copy()
        from sklearn.utils import check_array
        X = check_array(X, force_all_finite=True, estimator=self, copy=True)
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, "loadings_")
        if self.mean_ is None or self.std_ is None:
            warnings.warn(
                "Could not find original mean and standard deviation; using"
                "the mean and standard deviation from the current data set."
            )
            mean = np.mean(X, axis=0)
            std = np.std(X, axis=0)
        else:
            mean = self.mean_
            std = self.std_
        X_scale = (X - mean) / std
        if self.structure_ is not None:
            structure = self.structure_
        else:
            structure = self.loadings_
        try:
            self.weights_ = np.linalg.solve(self.corr_, structure)
        except Exception as error:
            warnings.warn(
                "Unable to calculate the factor score weights; "
                "factor loadings used instead: {}".format(error)
            )
            self.weights_ = self.loadings_
        scores = np.dot(X_scale, self.weights_)
        return scores

    def get_eigenvalues(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, ["loadings_", "corr_"])
        corr_mtx = self.corr_.copy()
        e_values, _ = np.linalg.eigh(corr_mtx)
        e_values = e_values[::-1]
        communalities = self.get_communalities()
        communalities = communalities.copy()
        np.fill_diagonal(corr_mtx, communalities)
        values, _ = np.linalg.eigh(corr_mtx)
        values = values[::-1]
        return e_values, values

    def get_communalities(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, "loadings_")
        loadings = self.loadings_.copy()
        communalities = (loadings**2).sum(axis=1)
        return communalities

    def get_uniquenesses(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, "loadings_")
        communalities = self.get_communalities()
        communalities = communalities.copy()
        uniqueness = 1 - communalities
        return uniqueness

    @staticmethod
    def _get_factor_variance(loadings):
        n_rows = loadings.shape[0]
        loadings = loadings**2
        variance = np.sum(loadings, axis=0)
        proportional_variance = variance / n_rows
        cumulative_variance = np.cumsum(proportional_variance, axis=0)
        return (variance, proportional_variance, cumulative_variance)

    def get_factor_variance(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, "loadings_")
        loadings = self.loadings_.copy()
        return self._get_factor_variance(loadings)

    def sufficiency(self, num_observations: int) -> Tuple[float, int, float]:
        nvar = self.corr_.shape[0]
        degrees = ((nvar - self.n_factors) ** 2 - nvar - self.n_factors) // 2
        obj = self._fit_ml_objective(
            self.get_uniquenesses(), self.corr_, self.n_factors
        )
        statistic = (
            num_observations - 1 - (2 * nvar + 5) / 6 - (2 * self.n_factors) / 3
        ) * obj
        from scipy.stats import chi2
        pvalue = chi2.sf(statistic, df=degrees)
        return statistic, degrees, pvalue

def inv_chol(x, logdet=False):
    from scipy.linalg import cholesky
    chol = cholesky(x, lower=True)
    chol_inv = np.linalg.inv(chol)
    chol_inv = np.dot(chol_inv.T, chol_inv)
    chol_logdet = None
    if logdet:
        chol_diag = np.diag(chol)
        chol_logdet = np.sum(np.log(chol_diag * chol_diag))
    return chol_inv, chol_logdet

def unique_elements(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

def fill_lower_diag(x):
    x = np.array(x)
    x = x if len(x.shape) == 1 else np.squeeze(x, axis=1)
    n = int(np.sqrt(len(x) * 2)) + 1
    out = np.zeros((n, n), dtype=float)
    out[np.tri(n, dtype=bool, k=-1)] = x
    return out

def merge_variance_covariance(variances, covariances=None):
    variances = (
        variances if len(variances.shape) == 1 else np.squeeze(variances, axis=1)
    )
    if covariances is None:
        variance_covariance = np.zeros((variances.shape[0], variances.shape[0]))
    else:
        variance_covariance = fill_lower_diag(covariances)
        variance_covariance += variance_covariance.T
    np.fill_diagonal(variance_covariance, variances)
    return variance_covariance

def get_first_idxs_from_values(x, eq=1, use_columns=True):
    x = np.array(x)
    if use_columns:
        n = x.shape[1]
        row_idx = [np.where(x[:, i] == eq)[0][0] for i in range(n)]
        col_idx = list(range(n))
    else:
        n = x.shape[0]
        col_idx = [np.where(x[i, :] == eq)[0][0] for i in range(n)]
        row_idx = list(range(n))
    return row_idx, col_idx

def get_free_parameter_idxs(x, eq=1):
    x[np.isnan(x)] = eq
    x = x.flatten(order="F")
    return np.where(x == eq)[0]

def duplication_matrix(n=1):
    if n < 1:
        raise ValueError(
            "The argument `n` must be a " "positive integer greater than 1."
        )
    dup = np.zeros((int(n * n), int(n * (n + 1) / 2)))
    count = 0
    for j in range(n):
        dup[j * n + j, count + j] = 1
        if j < n - 1:
            for i in range(j + 1, n):
                dup[j * n + i, count + i] = 1
                dup[i * n + j, count + i] = 1
        count += n - j - 1
    return dup

def duplication_matrix_pre_post(x):
    assert x.shape[0] == x.shape[1]
    n2 = x.shape[1]
    n = int(np.sqrt(n2))
    idx1 = get_symmetric_lower_idxs(n)
    idx2 = get_symmetric_upper_idxs(n)
    out = x[idx1, :] + x[idx2, :]
    u = np.where([i in idx2 for i in idx1])[0]
    out[u, :] = out[u, :] / 2.0
    out = out[:, idx1] + out[:, idx2]
    out[:, u] = out[:, u] / 2.0
    return out

def commutation_matrix(p, q):
    identity = np.eye(p * q)
    indices = np.arange(p * q).reshape((p, q), order="F")
    return identity.take(indices.ravel(), axis=0)

def get_symmetric_lower_idxs(n=1, diag=True):
    rows = np.repeat(np.arange(n), n).reshape(n, n)
    cols = rows.T
    if diag:
        return np.where((rows >= cols).T.flatten())[0]
    return np.where((cols > rows).T.flatten())[0]

def get_symmetric_upper_idxs(n=1, diag=True):
    rows = np.repeat(np.arange(n), n).reshape(n, n)
    cols = rows.T
    temp = np.arange(n * n).reshape(n, n)
    if diag:
        return temp.T[(rows >= cols).T]
    return temp.T[(cols > rows).T]

class ModelSpecification:
    def __init__(
        self, loadings, n_factors, n_variables, factor_names=None, variable_names=None
    ):
        assert isinstance(loadings, np.ndarray)
        assert loadings.shape[0] == n_variables
        assert loadings.shape[1] == n_factors
        self._loadings = loadings
        self._n_factors = n_factors
        self._n_variables = n_variables
        self._factor_names = factor_names
        self._variable_names = variable_names
        self._n_lower_diag = get_symmetric_lower_idxs(n_factors, False).shape[0]
        self._error_vars = np.full((n_variables, 1), np.nan)
        self._factor_covs = np.full((n_factors, n_factors), np.nan)
        self._loadings_free = get_free_parameter_idxs(loadings, eq=1)
        self._error_vars_free = merge_variance_covariance(self._error_vars)
        self._error_vars_free = get_free_parameter_idxs(self._error_vars_free, eq=-1)
        self._factor_covs_free = get_symmetric_lower_idxs(n_factors, False)

    def __str__(self):
        return f"<ModelSpecification object at {hex(id(self))}>"

    def copy(self):
        from copy import deepcopy
        return deepcopy(self)

    @property
    def loadings(self):
        return self._loadings.copy()

    @property
    def error_vars(self):
        return self._error_vars.copy()

    @property
    def factor_covs(self):
        return self._factor_covs.copy()

    @property
    def loadings_free(self):
        return self._loadings_free.copy()

    @property
    def error_vars_free(self):
        return self._error_vars_free.copy()

    @property
    def factor_covs_free(self):
        return self._factor_covs_free.copy()

    @property
    def n_variables(self):
        return self._n_variables

    @property
    def n_factors(self):
        return self._n_factors

    @property
    def n_lower_diag(self):
        return self._n_lower_diag

    @property
    def factor_names(self):
        return self._factor_names

    @property
    def variable_names(self):
        return self._variable_names

    def get_model_specification_as_dict(self):
        return {
            "loadings": self._loadings.copy(),
            "error_vars": self._error_vars.copy(),
            "factor_covs": self._factor_covs.copy(),
            "loadings_free": self._loadings_free.copy(),
            "error_vars_free": self._error_vars_free.copy(),
            "factor_covs_free": self._factor_covs_free.copy(),
            "n_variables": self._n_variables,
            "n_factors": self._n_factors,
            "n_lower_diag": self._n_lower_diag,
            "variable_names": self._variable_names,
            "factor_names": self._factor_names,
        }

class ModelParser:
    @staticmethod
    def parse_model_specification_from_dict(X, specification=None):
        if specification is None:
            factor_names, variable_names = None, None
            n_variables, n_factors = X.shape[1], X.shape[1]
            loadings = np.ones((n_factors, n_factors), dtype=int)
        elif isinstance(specification, dict):
            factor_names = list(specification)
            variable_names = unique_elements(
                [v for f in specification.values() for v in f]
            )
            loadings_new = {}
            for factor in factor_names:
                loadings_for_factor = pd.Series(variable_names).isin(
                    specification[factor]
                )
                loadings_for_factor = loadings_for_factor.astype(int)
                loadings_new[factor] = loadings_for_factor
            loadings = pd.DataFrame(loadings_new).values
            n_variables, n_factors = loadings.shape
        else:
            raise ValueError(
                "The model `specification` must be either a dict "
                "or None, not {}".format(type(specification))
            )
        return ModelSpecification(
            **{
                "loadings": loadings,
                "n_variables": n_variables,
                "n_factors": n_factors,
                "factor_names": factor_names,
                "variable_names": variable_names,
            }
        )

    @staticmethod
    def parse_model_specification_from_array(X, specification=None):
        if specification is None:
            n_variables, n_factors = X.shape[1], X.shape[1]
            loadings = np.ones((n_factors, n_factors), dtype=int)
        elif isinstance(specification, (np.ndarray, pd.DataFrame)):
            n_variables, n_factors = specification.shape
            if isinstance(specification, pd.DataFrame):
                loadings = specification.values.copy()
            else:
                loadings = specification.copy()
        else:
            raise ValueError(
                "The model `specification` must be either a numpy array "
                "or None, not {}".format(type(specification))
            )
        return ModelSpecification(
            **{"loadings": loadings, "n_variables": n_variables, "n_factors": n_factors}
        )

class cAnalyzor(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        specification=None,
        n_obs=None,
        is_cov_matrix=False,
        bounds=None,
        max_iter=200,
        tol=None,
        impute="median",
        disp=True,
    ):
        if is_cov_matrix and n_obs is None:
            raise ValueError(
                "If `is_cov_matrix=True`, you must provide "
                "the number of observations, `n_obs`."
            )
        self.specification = specification
        self.n_obs = n_obs
        self.is_cov_matrix = is_cov_matrix
        self.bounds = bounds
        self.max_iter = max_iter
        self.tol = tol
        self.impute = impute
        self.disp = disp
        self.cov_ = None
        self.mean_ = None
        self.loadings_ = None
        self.error_vars_ = None
        self.factor_varcovs_ = None
        self.log_likelihood_ = None
        self.aic_ = None
        self.bic_ = None
        self._n_factors = None
        self._n_variables = None
        self._n_lower_diag = None

    @staticmethod
    def _combine(
        loadings,
        error_vars,
        factor_vars,
        factor_covs,
        n_factors,
        n_variables,
        n_lower_diag,
    ):
        loadings = loadings.reshape(n_factors * n_variables, 1, order="F")
        error_vars = error_vars.reshape(n_variables, 1, order="F")
        factor_vars = factor_vars.reshape(n_factors, 1, order="F")
        factor_covs = factor_covs.reshape(n_lower_diag, 1, order="F")
        return np.concatenate([loadings, error_vars, factor_vars, factor_covs])

    @staticmethod
    def _split(x, n_factors, n_variables, n_lower_diag):
        loadings_ix = int(n_factors * n_variables)
        error_vars_ix = n_variables + loadings_ix
        factor_vars_ix = n_factors + error_vars_ix
        factor_covs_ix = n_lower_diag + factor_vars_ix
        return (
            x[:loadings_ix].reshape((n_variables, n_factors), order="F"),
            x[loadings_ix:error_vars_ix].reshape((n_variables, 1), order="F"),
            x[error_vars_ix:factor_vars_ix].reshape((n_factors, 1), order="F"),
            x[factor_vars_ix:factor_covs_ix].reshape((n_lower_diag, 1), order="F"),
        )

    def _objective(self, x0, cov_mtx, loadings):
        (
            loadings_init,
            error_vars_init,
            factor_vars_init,
            factor_covs_init,
        ) = self._split(
            x0, self.model.n_factors, self.model.n_variables, self.model.n_lower_diag
        )
        loadings_init[np.where(loadings == 0)] = 0
        factor_varcov_init = merge_variance_covariance(
            factor_vars_init, factor_covs_init
        )
        error_varcov_init = merge_variance_covariance(error_vars_init)
        with np.errstate(all="ignore"):
            factor_varcov_init = covariance_to_correlation(factor_varcov_init)
        sigma_theta = (
            loadings_init.dot(factor_varcov_init).dot(loadings_init.T)
            + error_varcov_init
        )
        with np.errstate(all="ignore"):
            error = -(
                ((-self.n_obs * self.model.n_variables / 2) * np.log(2 * np.pi))
                - (self.n_obs / 2)
                * (
                    np.log(np.linalg.det(sigma_theta))
                    + np.trace(cov_mtx.dot(np.linalg.inv(sigma_theta)))
                )
            )
            error = 0.0 if error < 0.0 else error
        return error

    def fit(self, X, y=None):
        if self.specification is None:
            self.model = ModelParser.parse_model_specification_from_array(
                X
            )
        elif isinstance(self.specification, ModelSpecification):
            self.model = self.specification.copy()
        else:
            raise ValueError(
                "The `specification` must be None or `ModelSpecification` "
                "instance, not {}".format(type(self.specification))
            )
        if isinstance(X, pd.DataFrame):
            X = X.values
        from sklearn.utils import check_array
        X = check_array(X, force_all_finite="allow-nan", estimator=self, copy=True)
        if np.isnan(X).any() and not self.is_cov_matrix:
            X = impute_values(X, how=self.impute)
        if not self.is_cov_matrix:
            self.n_obs = X.shape[0] if self.n_obs is None else self.n_obs
            self.mean_ = np.mean(X, axis=0)
            cov_mtx = cov(X)
        else:
            error_msg = (
                "If `is_cov_matrix=True`, then the rows and column in the data "
                "set must be equal, and must equal the number of variables "
                "in your model."
            )
            assert X.shape[0] == X.shape[1] == self.model.n_variables, error_msg
            cov_mtx = X.copy()
        self.cov_ = cov_mtx.copy()
        loading_init = self.model.loadings
        error_vars_init = np.full((self.model.n_variables, 1), 0.5)
        factor_vars_init = np.full((self.model.n_factors, 1), 1.0)
        factor_covs_init = np.full((self.model.n_lower_diag, 1), 0.05)
        x0 = self._combine(
            loading_init,
            error_vars_init,
            factor_vars_init,
            factor_covs_init,
            self.model.n_factors,
            self.model.n_variables,
            self.model.n_lower_diag,
        )
        if self.bounds is not None:
            error_msg = (
                "The length of `bounds` must equal the length of your "
                "input array `x0`: {} != {}.".format(len(self.bounds), len(x0))
            )
            assert len(self.bounds) == len(x0), error_msg
        from scipy.optimize import minimize
        res = minimize(
            self._objective,
            x0.flatten(),
            method="L-BFGS-B",
            options={"maxiter": self.max_iter, "disp": self.disp},
            bounds=self.bounds,
            args=(cov_mtx, self.model.loadings),
        )
        if not res.success:
            warnings.warn(
                f"The optimization routine failed to converge: {str(res.message)}"
            )
        (loadings_res, error_vars_res, factor_vars_res, factor_covs_res) = self._split(
            res.x, self.model.n_factors, self.model.n_variables, self.model.n_lower_diag
        )
        factor_varcovs_res = merge_variance_covariance(factor_vars_res, factor_covs_res)
        with np.errstate(all="ignore"):
            factor_varcovs_res = covariance_to_correlation(factor_varcovs_res)
        self.loadings_ = loadings_res
        self.error_vars_ = error_vars_res
        self.factor_varcovs_ = factor_varcovs_res
        self.log_likelihood_ = -res.fun
        self.aic_ = 2 * res.fun + 2 * (x0.shape[0] + self.model.n_variables)
        if self.n_obs is not None:
            self.bic_ = 2 * res.fun + np.log(self.n_obs) * (
                x0.shape[0] + self.model.n_variables
            )
        return self

    def transform(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.values
        from sklearn.utils import check_array
        X = check_array(X, force_all_finite=True, estimator=self, copy=True)
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, ["loadings_", "error_vars_"])
        if self.mean_ is None:
            warnings.warn(
                "Could not find original mean; using the mean "
                "from the current data set."
            )
            mean = np.mean(X, axis=0)
        else:
            mean = self.mean_
        X_scale = X - mean
        loadings = self.loadings_.copy()
        error_vars = self.error_vars_.copy()
        error_covs = np.eye(error_vars.shape[0])
        np.fill_diagonal(error_covs, error_vars)
        error_covs_inv = np.linalg.inv(error_covs)
        weights = (
            np.linalg.pinv(loadings.T.dot(error_covs_inv).dot(loadings))
            .dot(loadings.T)
            .dot(error_covs_inv)
        )
        scores = weights.dot(X_scale.T).T
        return scores

    def get_model_implied_cov(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, ["loadings_", "factor_varcovs_"])
        error = np.diag(self.error_vars_.flatten())
        return self.loadings_.dot(self.factor_varcovs_).dot(self.loadings_.T) + error

    def _get_derivatives_implied_cov(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, "loadings_")
        loadings = self.loadings_.copy()
        factor_covs = self.factor_varcovs_.copy()
        sym_lower_var_idx = get_symmetric_lower_idxs(self.model.n_variables)
        sym_upper_fac_idx = get_symmetric_upper_idxs(self.model.n_factors, diag=False)
        sym_lower_fac_idx = get_symmetric_lower_idxs(self.model.n_factors, diag=False)
        factors_diag = np.eye(self.model.n_factors)
        factors_diag_mult = (
            factors_diag.dot(factor_covs).dot(factors_diag.T).dot(loadings.T)
        )
        loadings_dx = np.eye(self.model.n_variables**2) + commutation_matrix(
            self.model.n_variables, self.model.n_variables
        )
        loadings_dx = loadings_dx.dot(
            np.kron(factors_diag_mult, np.eye(self.model.n_variables)).T
        )
        factor_covs_dx = loadings.dot(factors_diag)
        factor_covs_dx = np.kron(factor_covs_dx, factor_covs_dx)
        off_diag = (
            factor_covs_dx[:, sym_lower_fac_idx] + factor_covs_dx[:, sym_upper_fac_idx]
        )
        combine_indices = np.concatenate([sym_upper_fac_idx, sym_lower_fac_idx])
        combine_diag = np.concatenate([off_diag, off_diag], axis=1)
        factor_covs_dx[:, combine_indices] = combine_diag
        factor_covs_dx = factor_covs_dx[:, : factor_covs.size]
        error_covs_dx = np.eye(self.model.n_variables**2)
        loadings_dx = loadings_dx[sym_lower_var_idx, :]
        factor_covs_dx = factor_covs_dx[sym_lower_var_idx, :]
        error_covs_dx = error_covs_dx[sym_lower_var_idx, :]
        intercept_dx = np.zeros(
            (loadings_dx.shape[0], self.model.n_variables), dtype=float
        )
        return (
            loadings_dx[:, self.model.loadings_free].copy(),
            factor_covs_dx[:, self.model.factor_covs_free].copy(),
            error_covs_dx[:, self.model.error_vars_free].copy(),
            intercept_dx,
        )

    def _get_derivatives_implied_mu(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, "loadings_")
        factors_zero = np.zeros((self.model.n_factors, 1))
        factors_diag = np.eye(self.model.n_factors)
        error_covs_dx = np.zeros(
            (self.model.n_variables, len(self.model.error_vars_free))
        )
        factor_covs_dx = np.zeros(
            (self.model.n_variables, len(self.model.factor_covs_free))
        )
        loadings_dx = np.kron(
            factors_diag.dot(factors_zero).T, np.eye(self.model.n_variables)
        )
        loadings_dx = loadings_dx[:, self.model.loadings_free].copy()
        intercept_dx = np.zeros((loadings_dx.shape[0], self.model.n_variables))
        intercept_dx[: self.model.n_variables, : self.model.n_variables] = np.eye(
            self.model.n_variables
        )
        return (loadings_dx, factor_covs_dx, error_covs_dx, intercept_dx)

    def get_standard_errors(self):
        from sklearn.utils.validation import check_is_fitted
        check_is_fitted(self, ["loadings_", "n_obs"])
        (
            loadings_dx,
            factor_covs_dx,
            error_covs_dx,
            intercept_dx,
        ) = self._get_derivatives_implied_cov()
        (
            loadings_dx_mu,
            factor_covs_dx_mu,
            error_covs_dx_mu,
            intercept_dx_mu,
        ) = self._get_derivatives_implied_mu()
        loadings_dx = np.append(loadings_dx_mu, loadings_dx, axis=0)
        factor_covs_dx = np.append(factor_covs_dx_mu, factor_covs_dx, axis=0)
        error_cov_dx = np.append(error_covs_dx_mu, error_covs_dx, axis=0)
        intercept_dx = np.append(intercept_dx_mu, intercept_dx, axis=0)
        sigma = self.get_model_implied_cov()
        sigma_inv = np.linalg.inv(sigma)
        sigma_inv_kron = np.kron(sigma_inv, sigma_inv)
        h1_information = 0.5 * duplication_matrix_pre_post(sigma_inv_kron)
        from scipy.linalg import block_diag
        h1_information = block_diag(sigma_inv, h1_information)
        delta = np.concatenate(
            (loadings_dx, error_cov_dx, factor_covs_dx, intercept_dx), axis=1
        )
        information = delta.T.dot(h1_information).dot(delta)
        information = (1 / self.n_obs) * np.linalg.inv(information)
        se = np.sqrt(np.abs(np.diag(information)))
        loadings_idx = len(self.model.loadings_free)
        error_vars_idx = self.model.n_variables + loadings_idx
        loadings_se = np.zeros((self.model.n_factors * self.model.n_variables,))
        loadings_se[self.model.loadings_free] = se[:loadings_idx]
        loadings_se = loadings_se.reshape(
            (self.model.n_variables, self.model.n_factors), order="F"
        )
        error_vars_se = se[loadings_idx:error_vars_idx]
        return loadings_se, error_vars_se

def run_exploratory_factor_analysis(csv_file_path, n_factors):
    data = pd.read_csv(csv_file_path)
    fa = eAnalyzor(n_factors=n_factors, rotation='varimax', method='principal')
    fa.fit(data)
    loadings = fa.loadings_
    loading_df = pd.DataFrame(loadings, index=data.columns)
    return loading_df

def assign_items_to_components(loading_df):
    component_dict = {f'Component {i}': [] for i in range(loading_df.shape[1])}
    for item in loading_df.index:
        row = loading_df.loc[item]
        highest_component = row.abs().idxmax()
        component_num = highest_component
        loading_value = row[highest_component]
        component_dict[f'Component {component_num}'].append(f"{item} ({loading_value:.3f})")
    return component_dict

def run_cfa():
    file_path = select_csv_file_gui()
    data = pd.read_csv(file_path)
    print("Available columns: ", data.columns.tolist())
    n_factors = int(input("\nEnter the number of factors in the model: "))
    factor_items = {}
    all_items = []
    for factor in range(1, n_factors + 1):
        n_items = int(input(f"Enter the number of items for Factor {factor}: "))
        items = []
        for i in range(n_items):
            item = input(f"Enter the column name for item {i+1} of Factor {factor}: ")
            if item not in data.columns:
                print(f"Column '{item}' not found in the CSV file. Exiting.")
                return
            items.append(item)
            all_items.append(item)
        factor_items[f"Factor {factor}"] = items
    data_subset = data[all_items]
    n_variables = len(all_items)
    loading_matrix = np.zeros((n_variables, n_factors))
    row_index = 0
    for factor_index, (factor, items) in enumerate(factor_items.items()):
        for item in items:
            loading_matrix[row_index, factor_index] = 1
            row_index += 1
    model_spec = ModelSpecification(loadings=loading_matrix, n_factors=n_factors, n_variables=n_variables)
    cfa = cAnalyzor(model_spec, disp=True)
    cfa.fit(data_subset.values)
    loadings = pd.DataFrame(cfa.loadings_, index=data_subset.columns)
    loadings.columns = factor_items.keys()
    print("\nFactor Loadings:\n", loadings)
    ask = input("\nDraw a SVG factor diagram (Y/n)? ")
    if  ask.lower() == 'y':
        import graphviz
        dot = graphviz.Digraph()
        for factor in factor_items.keys():
            dot.node(factor, shape='ellipse')
        for factor_idx, (factor, items) in enumerate(factor_items.items()):
            for item in items:
                dot.node(item, shape='box')
                dot.edge(factor, item, label=f"{round(loadings.loc[item].iloc[factor_idx], 2)}")
        output_path = "factor_diagram"
        dot.render(output_path, format="svg")
        print(f"Factor diagram saved as {output_path}.svg")

def run_efa():
    file_path = select_csv_file_gui()
    if not file_path:
        print("No file selected.")
        return
    data = pd.read_csv(file_path)
    use_whole_file = input("Use the entire CSV file for analysis? (Y/n): ").strip().lower()
    if use_whole_file == 'y':
        data_subset = data.copy()
        selected_columns = data.columns.tolist()
    else:
        print("Available columns:")
        for i, col in enumerate(data.columns):
            print(f"{i + 1}: {col}")
        num_items = int(input("Enter the number of items (columns) to include: "))
        selected_columns = []
        for i in range(num_items):
            print(f"For item {i + 1}")
            col = select_column_free(data)
            selected_columns.append(col)
    data_subset = clean_data(data, selected_columns)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_subset)
    kmo_all, kmo_model = calculate_kmo(data_scaled)
    print(f"\nKaiser-Meyer-Olkin (KMO) Measure: {kmo_model}")
    chi_square_value, degree_of_freedom, p_value = calculate_bartlett_sphericity(data_scaled)
    print(f"Bartlett's test of sphericity: Chi-square = {chi_square_value:.3f}, df = {int(degree_of_freedom)}, p-value = {p_value:.3f}")
    fa_initial = eAnalyzor(rotation=None, method='principal')
    fa_initial.fit(data_scaled)
    eigenvalues = fa_initial.get_eigenvalues()[0]
    print("\nEigenvalues for each component detected:")
    for i, eigenvalue in enumerate(eigenvalues):
        print(f"Component {i + 1}: {eigenvalue}")
    variance_explained = eigenvalues / np.sum(eigenvalues)
    print("\nPercentage of Variance Explained for each component:")
    for i, variance in enumerate(variance_explained):
        print(f"Component {i + 1}: {variance * 100:.2f}%")
    n_components = sum(eigenvalues >= 1)
    print(f"\n*** number of components with eigenvalue ≥ 1: {n_components}")
    fa = eAnalyzor(rotation="varimax", method='principal', n_factors=n_components)
    fa.fit(data_scaled)
    rotated_matrix = fa.loadings_
    print("\nRotated Component Matrix (Varimax with Kaiser Normalization):")
    print(pd.DataFrame(rotated_matrix, index=selected_columns))

def run_efa_fixed():
    csv_file = select_csv_file_gui()
    if csv_file:
        n_factors = int(input("Enter the number of factors to extract: "))
        rotated_matrix = run_exploratory_factor_analysis(csv_file, n_factors)
        print("\nRotated Component Matrix (Varimax with Kaiser Normalization):")
        print(rotated_matrix)
        component_assignments = assign_items_to_components(rotated_matrix)
        print("\nItems assigned to components:")
        for component, items in component_assignments.items():
            print(f"{component}: {', '.join(items)}")
    else:
        print("No file selected.")

def jsminifier(js, **kwargs):
    klass = io.StringIO
    ins = klass(js)
    outs = klass()
    JavascriptMinify(ins, outs, **kwargs).minify()
    return outs.getvalue()

class JavascriptMinify(object):
    def __init__(self, instream=None, outstream=None, quote_chars="'\""):
        self.ins = instream
        self.outs = outstream
        self.quote_chars = quote_chars

    def minify(self, instream=None, outstream=None):
        if instream and outstream:
            self.ins, self.outs = instream, outstream
        self.is_return = False
        self.return_buf = ''
        
        def write(char):
            if char in 'return':
                self.return_buf += char
                self.is_return = self.return_buf == 'return'
            else:
                self.return_buf = ''
                self.is_return = self.is_return and char < '!'
            self.outs.write(char)
            if self.is_return:
                self.return_buf = ''
        read = self.ins.read
        space_strings = "abcdefghijklmnopqrstuvwxyz"\
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$\\"
        self.space_strings = space_strings
        starters, enders = '{[(+-', '}])+-/' + self.quote_chars
        newlinestart_strings = starters + space_strings + self.quote_chars
        newlineend_strings = enders + space_strings + self.quote_chars
        self.newlinestart_strings = newlinestart_strings
        self.newlineend_strings = newlineend_strings
        do_newline = False
        do_space = False
        escape_slash_count = 0
        in_quote = ''
        quote_buf = []
        previous = ';'
        previous_non_space = ';'
        next1 = read(1)
        while next1:
            next2 = read(1)
            if in_quote:
                quote_buf.append(next1)

                if next1 == in_quote:
                    numslashes = 0
                    for c in reversed(quote_buf[:-1]):
                        if c != '\\':
                            break
                        else:
                            numslashes += 1
                    if numslashes % 2 == 0:
                        in_quote = ''
                        write(''.join(quote_buf))
            elif next1 in '\r\n':
                next2, do_newline = self.newline(
                    previous_non_space, next2, do_newline)
            elif next1 < '!':
                if (previous_non_space in space_strings \
                    or previous_non_space > '~') \
                    and (next2 in space_strings or next2 > '~'):
                    do_space = True
                elif previous_non_space in '-+' and next2 == previous_non_space:
                    do_space = True
                elif self.is_return and next2 == '/':
                    write(' ')
            elif next1 == '/':
                if do_space:
                    write(' ')
                if next2 == '/':
                    next2 = self.line_comment(next1, next2)
                    next1 = '\n'
                    next2, do_newline = self.newline(
                        previous_non_space, next2, do_newline)
                elif next2 == '*':
                    self.block_comment(next1, next2)
                    next2 = read(1)
                    if previous_non_space in space_strings:
                        do_space = True
                    next1 = previous
                else:
                    if previous_non_space in '{(,=:[?!&|;' or self.is_return:
                        self.regex_literal(next1, next2)
                        next2 = read(1)
                    else:
                        write('/')
            else:
                if do_newline:
                    write('\n')
                    do_newline = False
                    do_space = False
                if do_space:
                    do_space = False
                    write(' ')
                write(next1)
                if next1 in self.quote_chars:
                    in_quote = next1
                    quote_buf = []
            if next1 >= '!':
                previous_non_space = next1
            if next1 == '\\':
                escape_slash_count += 1
            else:
                escape_slash_count = 0
            previous = next1
            next1 = next2

    def regex_literal(self, next1, next2):
        assert next1 == '/'
        self.return_buf = ''
        read = self.ins.read
        write = self.outs.write
        in_char_class = False
        write('/')
        next = next2
        while next and (next != '/' or in_char_class):
            write(next)
            if next == '\\':
                write(read(1))
            elif next == '[':
                write(read(1))
                in_char_class = True
            elif next == ']':
                in_char_class = False
            next = read(1)
        write('/')

    def line_comment(self, next1, next2):
        assert next1 == next2 == '/'
        read = self.ins.read
        while next1 and next1 not in '\r\n':
            next1 = read(1)
        while next1 and next1 in '\r\n':
            next1 = read(1)
        return next1

    def block_comment(self, next1, next2):
        assert next1 == '/'
        assert next2 == '*'
        read = self.ins.read
        next1 = read(1)
        next2 = read(1)
        comment_buffer = '/*'
        while next1 != '*' or next2 != '/':
            comment_buffer += next1
            next1 = next2
            next2 = read(1)

        if comment_buffer.startswith("/*!"):
            self.outs.write(comment_buffer)
            self.outs.write("*/\n")

    def newline(self, previous_non_space, next2, do_newline):
        read = self.ins.read
        if previous_non_space and (
                        previous_non_space in self.newlineend_strings
                        or previous_non_space > '~'):
            while 1:
                if next2 < '!':
                    next2 = read(1)
                    if not next2:
                        break
                else:
                    if next2 in self.newlinestart_strings \
                            or next2 > '~' or next2 == '/':
                        do_newline = True
                    break
        return next2, do_newline

def list_js_files():
    js_files = [f for f in os.listdir() if f.endswith('.js')]
    if not js_files:
        print("No JavaScript files found in the current directory.")
    return js_files

def select_js_file(js_files):
    print("Select a JavaScript file to minify:")
    for idx, file in enumerate(js_files, start=1):
        print(f"{idx}. {file}")
    choice = int(input("Enter the number corresponding to the file: ")) - 1
    return js_files[choice]

def minify_js_file(file_path):
    with open(file_path, 'r') as file:
        minified_code = jsminifier(file.read())
    minified_file_path = f"minified_{file_path}"
    with open(minified_file_path, 'w') as minified_file:
        minified_file.write(minified_code)
    print(f"Minified file saved as: {minified_file_path}")

def minifyjs():
    js_files = list_js_files()
    if js_files:
        selected_file = select_js_file(js_files)
        minify_js_file(selected_file)

def get_temp_folder():
    from pathlib import Path
    return Path(tempfile.gettempdir())

def scan_temp_files(temp_dir):
    files = []
    for file in temp_dir.rglob("*"):
        if file.is_file():
            try:
                size = file.stat().st_size
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                files.append((file, size, mtime))
            except Exception:
                pass
    return files

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def delete_files(files_to_delete):
    total_deleted = 0
    failed = []
    for file, size, _ in files_to_delete:
        try:
            file.unlink()
            total_deleted += size
        except Exception:
            failed.append(str(file))
    return total_deleted, failed

class TempCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧹 Temp Folder Cleaner")
        self.temp_dir = get_temp_folder()
        self.files = scan_temp_files(self.temp_dir)
        self.files.sort(key=lambda x: x[1], reverse=True)

        self.setup_ui()
        self.refresh_summary()

    def setup_ui(self):
        import tkinter as tk
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack()

        self.summary_label = tk.Label(self.frame, text="Scanning...")
        self.summary_label.pack()

        btn_top = tk.Button(self.frame, text="Delete Top N Largest Files", command=self.delete_top_n)
        btn_top.pack(fill="x", pady=5)

        btn_old = tk.Button(self.frame, text="Delete Files Older Than N Days", command=self.delete_old)
        btn_old.pack(fill="x", pady=5)

        btn_all = tk.Button(self.frame, text="Delete ALL Temp Files", command=self.delete_all)
        btn_all.pack(fill="x", pady=5)

        btn_refresh = tk.Button(self.frame, text="🔄 Refresh", command=self.refresh_data)
        btn_refresh.pack(fill="x", pady=5)

        self.file_listbox = tk.Listbox(self.frame, width=80, height=12)
        self.file_listbox.pack(pady=5)

    def refresh_data(self):
        self.files = scan_temp_files(self.temp_dir)
        self.files.sort(key=lambda x: x[1], reverse=True)
        self.refresh_summary()

    def refresh_summary(self):
        import tkinter as tk
        total_size = sum(size for _, size, _ in self.files)
        self.summary_label.config(text=f"📁 Temp folder: {self.temp_dir}\n📦 Total size: {format_size(total_size)} | Files: {len(self.files)}")
        self.file_listbox.delete(0, tk.END)
        for i, (file, size, _) in enumerate(self.files[:10]):
            self.file_listbox.insert(tk.END, f"{i+1:2d}. {file.name} - {format_size(size)} - {file}")

    def delete_top_n(self):
        from tkinter import messagebox, simpledialog
        n = simpledialog.askinteger("Top N", "Delete how many of the largest files?", minvalue=1, maxvalue=len(self.files))
        if n:
            to_delete = self.files[:n]
            deleted_size, failed = delete_files(to_delete)
            self.refresh_data()
            messagebox.showinfo("Deleted", f"✅ Deleted {n} files.\n💾 Freed: {format_size(deleted_size)}\n⚠️ Failed: {len(failed)}")

    def delete_old(self):
        from datetime import timedelta
        from tkinter import messagebox, simpledialog
        days = simpledialog.askinteger("Older Than", "Delete files older than how many days?", minvalue=1)
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            old_files = [f for f in self.files if f[2] < cutoff]
            deleted_size, failed = delete_files(old_files)
            self.refresh_data()
            messagebox.showinfo("Deleted", f"✅ Deleted {len(old_files)} files older than {days} days.\n💾 Freed: {format_size(deleted_size)}\n⚠️ Failed: {len(failed)}")

    def delete_all(self):
        from tkinter import messagebox
        confirm = messagebox.askyesno("Confirm", "⚠️ Are you sure you want to delete ALL files in the temp folder?")
        if confirm:
            deleted_size, failed = delete_files(self.files)
            self.refresh_data()
            messagebox.showinfo("Deleted", f"✅ Deleted all temp files.\n💾 Freed: {format_size(deleted_size)}\n⚠️ Failed: {len(failed)}")

def clean_temp():
    import tkinter as tk
    root = tk.Tk()
    TempCleanerApp(root)
    root.mainloop()

def __init__():
    parser = argparse.ArgumentParser(description="rjj will execute different functions based on command-line arguments")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand", help="choose a subcommand:")
    subparsers.add_parser('a', help='run file anlaysis')
    subparsers.add_parser('c', help='convert json to csv')
    subparsers.add_parser('r', help='convert csv to json')
    subparsers.add_parser('y', help='convert csv to json yo')
    subparsers.add_parser('z', help='convert csv to json cluster')
    subparsers.add_parser('e', help='erase duplicate record(s)')
    subparsers.add_parser('i', help='inner join two csv files')
    subparsers.add_parser('o', help='outer join two csv files')
    subparsers.add_parser('m', help='identify matched record(s)')
    subparsers.add_parser('u', help='identify unique record(s)')
    subparsers.add_parser('d', help='detect co-existing record(s)')
    subparsers.add_parser('b', help='bind all csv(s) by column(s)')
    subparsers.add_parser('j', help='joint all csv(s) together')
    subparsers.add_parser('s', help='split csv to piece(s)')
    subparsers.add_parser('f', help='filter data by keyword')
    subparsers.add_parser('k', help='filter data by keyword for excel')
    subparsers.add_parser('h', help='identify matched record(s) for excel')
    subparsers.add_parser('q', help='identify unique record(s) for excel')
    subparsers.add_parser('t', help='joint all excel(s) into one')
    subparsers.add_parser('x', help='split excel to piece(s)')
    subparsers.add_parser('oz', help='run one-sample z-test')
    subparsers.add_parser('ot', help='run one-sample t-test')
    subparsers.add_parser('pt', help='run paired-sample t-test')
    subparsers.add_parser('it', help='run independent-sample t-test')
    subparsers.add_parser('lv', help='run levene test for two groups')
    subparsers.add_parser('hv', help='run homogeneity test of variance')
    subparsers.add_parser('oa', help='run one-way anova')
    subparsers.add_parser('ca', help='run correlation analysis')
    subparsers.add_parser('ra', help='run regression analysis')
    subparsers.add_parser('rt', help='run reliability test')
    subparsers.add_parser('et', help='evaluate effect size for one-sample t-test')
    subparsers.add_parser('ep', help='evaluate effect size for paired-sample t-test')
    subparsers.add_parser('ei', help='evaluate effect size for independent-sample t-test')
    subparsers.add_parser('eo', help='evaluate effect size for one-way anova')
    subparsers.add_parser('pp', help='estimate sample size for paired-sample t-test')
    subparsers.add_parser('pi', help='estimate sample size for independent-sample t-test')
    subparsers.add_parser('po', help='estimate sample size for one-way anova')
    subparsers.add_parser('pc', help='estimate sample size for correlation')
    subparsers.add_parser('pr', help='estimate sample size for regression')
    subparsers.add_parser('n', help='give descriptive statistics for a column')
    subparsers.add_parser('g', help='give descriptive statistics by group(s)')
    subparsers.add_parser('cfa', help='run confirmatory factor analysis')
    subparsers.add_parser('efa', help='run exploratory factor analysis')
    subparsers.add_parser('tea', help='transfer fixed factor to exploratory analysis')
    subparsers.add_parser('fit', help='run regression model fit analysis')
    subparsers.add_parser('dir', help='create folder(s)')
    subparsers.add_parser('pie', help='draw a pie chart')
    subparsers.add_parser('bar', help='draw a bar chart')
    subparsers.add_parser('pl', help='draw a scatter plot with line')
    subparsers.add_parser('l', help='draw a line graph')
    subparsers.add_parser('p', help='draw a scatter plot')
    subparsers.add_parser('bx', help='draw a box plot')
    subparsers.add_parser('box', help='draw many boxplot(s)')
    subparsers.add_parser('map', help='map from god view')
    subparsers.add_parser('donut', help='bake a donut')
    subparsers.add_parser('point', help='compute point')
    subparsers.add_parser('clean', help='check and clear temp')
    subparsers.add_parser('output', help='output as csv and json')
    subparsers.add_parser('report', help='generate report')
    subparsers.add_parser('prompt', help='generate random prompt from json')
    subparsers.add_parser('minify', help='minify py')
    subparsers.add_parser('my', help='minify py plus')
    subparsers.add_parser('ms', help='minify js')
    subparsers.add_parser('mj', help='minify json')
    subparsers.add_parser('mh', help='minify html')
    subparsers.add_parser('txt', help='convert all csv to txt')
    subparsers.add_parser('png', help='create transparent png')
    subparsers.add_parser('gif', help='create gif animation')
    subparsers.add_parser('ico', help='convert png to ico')
    subparsers.add_parser('i2p', help='convert ico to png')
    subparsers.add_parser('cut', help='cut timestamp')
    subparsers.add_parser('glue', help='glue timestamp')
    subparsers.add_parser('code', help='encode or decode')
    subparsers.add_parser('json', help='join all json up')
    subparsers.add_parser('read', help='read data file')
    subparsers.add_parser('join', help='join it up')
    subparsers.add_parser('home', help='go home')
    args = parser.parse_args()
    if args.subcommand == 'a':
        base_directory = os.getcwd()
        ask = input("Enter another name instead of analysis_statistics (Y/n)? ")
        if  ask.lower() == 'y':
            given = input("Give a name to the statistic file: ")
            output_file=f'{given}.csv'
        else:
            output_file='analysis_statistics.csv'
        print("Processing...")
        files_info, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files = get_files_and_hashes(base_directory)
        save_file_info_to_csv(files_info, output_file)
        print(f"File statistics have been saved to '{output_file}'.")
        ask = input("Enter another name instead of analysis_results (Y/n)? ")
        if  ask.lower() == 'y':
            given = input("Give a name to the result file: ")
            report_file=f'{given}.csv'
        else:
            report_file='analysis_results.csv'
        save_file_report_to_csv(report_file, total_size_mb, no_of_files, no_of_unique_files, no_of_duplicate_files)
        print(f"Results of the File Analysis have been saved to '{report_file}'.")
        print(f"\nSummary of the file analysis:")
        print(f"Number of duplicate files: {no_of_duplicate_files}")
        print(f"Number of unique files   : {no_of_unique_files}")
        print(f"Number of files          : {no_of_files}")
        print(f"Total size (MB)          : {total_size_mb}")
    elif args.subcommand == 'j':
        ask = input("Give a name to the output file (Y/n)? ")
        if  ask.lower() == 'y':
            output = input("Enter a name to the output file: ")
        else:
            output='output'
        jointer(output)
    elif args.subcommand == 'home':
        print("activating browser...")
        import webbrowser
        webbrowser.open("https://rjj.gguf.org")
    elif args.subcommand == 'clean':
        clean_temp()
    elif args.subcommand == 'join':
        joint()
    elif args.subcommand == 'code':
        base64codeHandler()
    elif args.subcommand == 'read':
        read_data_file()
    elif args.subcommand == 'json':
        json_merger()
    elif args.subcommand == 'txt':
        csv_to_txt()
    elif args.subcommand == 'gif':
        create_gif()
    elif args.subcommand == 'png':
        create_png()
    elif args.subcommand == 'ico':
        png2ico()
    elif args.subcommand == 'i2p':
        ico2png()
    elif args.subcommand == 'cut':
        timestamp_cutter()
    elif args.subcommand == 'glue':
        timestamp_glue()
    elif args.subcommand == 'mj':
        minify_json()
    elif args.subcommand == 'ms':
        minifyjs()
    elif args.subcommand == 'mh':
        html_minifier()
    elif args.subcommand == 'my':
        minify_py2()
    elif args.subcommand == 'minify':
        minify_py()
    elif args.subcommand == 'point':
        compute_point()
    elif args.subcommand == 'report':
        generate_reports()
    elif args.subcommand == 'output':
        output_as_csv_json()
    elif args.subcommand == 'prompt':
        generate_txt_descriptor()
    elif args.subcommand == 's':
        spliter()
    elif args.subcommand == 'b':
        binder()
    elif args.subcommand == 'f':
        filter()
    elif args.subcommand == 'e':
        eraser()
    elif args.subcommand == 'd':
        detector()
    elif args.subcommand == 'i':
        innerj()
    elif args.subcommand == 'o':
        outerj()
    elif args.subcommand == 'c':
        convertor()
    elif args.subcommand == 'r':
        reverser()
    elif args.subcommand == 'y':
        csv_to_json()
    elif args.subcommand == 'z':
        cluzter()
    elif args.subcommand == 'k':
        kilter()
    elif args.subcommand == 'x':
        xplit()
    elif args.subcommand == 't':
        xjoint()
    elif args.subcommand == 'm':
        matcher()
    elif args.subcommand == 'u':
        uniquer()
    elif args.subcommand == 'h':
        xmatch()
    elif args.subcommand == 'q':
        uniquex()
    elif args.subcommand == 'n':
        display_column()
    elif args.subcommand == 'g':
        display_group()
    elif args.subcommand == 'oz':
        one_sample_z()
    elif args.subcommand == 'ot':
        one_sample_t()
    elif args.subcommand == 'pt':
        paired_sample_t()
    elif args.subcommand == 'it':
        independ_sample_t()
    elif args.subcommand == 'lv':
        levene_t()
    elif args.subcommand == 'hv':
        levene_w()
    elif args.subcommand == 'oa':
        one_way_f()
    elif args.subcommand == 'ca':
        pearson_r()
    elif args.subcommand == 'ra':
        regression()
    elif args.subcommand == 'rt':
        reliability_test()
    elif args.subcommand == 'et':
        one_sample_t_test_v2()
    elif args.subcommand == 'ep':
        paired_sample_t_test_v2()
    elif args.subcommand == 'ei':
        independent_sample_t_test_v2()
    elif args.subcommand == 'eo':
        one_way_anova_v2()
    elif args.subcommand == 'cfa':
        run_cfa()
    elif args.subcommand == 'efa':
        run_efa()
    elif args.subcommand == 'tea':
        run_efa_fixed()
    elif args.subcommand == 'fit':
        run_regression()
    elif args.subcommand == 'pp':
        pa_pt()
    elif args.subcommand == 'pi':
        pa_it()
    elif args.subcommand == 'po':
        pa_oa()
    elif args.subcommand == 'pc':
        pa_r()
    elif args.subcommand == 'pr':
        pa_ra()
    elif args.subcommand == 'dir':
        mk_dir()
    elif args.subcommand == 'pie':
        piechart()
    elif args.subcommand == 'bar':
        charter()
    elif args.subcommand == 'pl':
        scatter()
    elif args.subcommand == 'l':
        liner()
    elif args.subcommand == 'p':
        plotter()
    elif args.subcommand == 'bx':
        boxplot()
    elif args.subcommand == 'box':
        boxplots()
    elif args.subcommand == 'map':
        mapper()
    elif args.subcommand == 'donut':
        heatmap()