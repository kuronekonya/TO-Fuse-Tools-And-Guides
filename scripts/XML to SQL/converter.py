import xml.etree.ElementTree as ET
from tkinter import Tk, filedialog, messagebox
import os
import math

# 75-column schema
COLUMNS = [
    "ID", "Class", "Type", "SubType", "ItemFType", "Name", "Comment", "Use", "Name_Eng", "Comment_Eng",
    "FileName", "BundleNum", "InvFileName", "InvBundleNum", "CmtFileName", "CmtBundleNum", "EquipFileName",
    "PivotID", "PaletteId", "Options", "HideHat", "ChrTypeFlags", "GroundFlags", "SystemFlags", "OptionsEx",
    "Weight", "Value", "MinLevel", "Effect", "EffectFlags2", "SelRange", "Life", "Depth", "Delay", "AP", "HP",
    "HPCon", "MP", "MPCon", "Money", "APPlus", "ACPlus", "DXPlus", "MaxMPPlus", "MAPlus", "MDPlus", "MaxWTPlus",
    "DAPlus", "LKPlus", "MaxHPPlus", "DPPlus", "HVPlus", "HPRecoveryRate", "MPRecoveryRate", "CardNum",
    "CardGenGrade", "CardGenParam", "DailyGenCnt", "PartFileName", "ChrFTypeFlag", "ChrGender", "ExistType",
    "Ncash", "NewCM", "FamCM", "Summary", "ShopFileName", "ShopBundleNum", "MinStatType", "MinStatLv",
    "RefineIndex", "RefineType", "CompoundSlot", "SetItemID", "ReformCount"
]
ESCAPED_COLUMNS = [f"[{col}]" if col.upper() == "USE" else col for col in COLUMNS]
STRING_FIELDS = {
    "Name", "Comment", "Use", "Name_Eng", "Comment_Eng", "FileName", "InvFileName", "CmtFileName",
    "EquipFileName", "PartFileName", "Summary", "ShopFileName", "Options"
}

def escape_sql_value(col, val):
    if not val or val.strip() == "":
        return "0"
    if col in STRING_FIELDS:
        return "N'" + val.replace("'", "''") + "'"
    try:
        float(val)
        return val
    except ValueError:
        return "N'" + val.replace("'", "''") + "'"

def extract_rows_from_xml(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        insert_statements = []

        for row in root.findall("ROW"):
            row_data = {el.tag: el.text.strip() if el.text else "" for el in row}
            values = [escape_sql_value(col, row_data.get(col, "")) for col in COLUMNS]
            sql = f"INSERT INTO dbo.ItemParam ({', '.join(ESCAPED_COLUMNS)}) VALUES (\n    {', '.join(values)}\n);"
            insert_statements.append(sql)
        return insert_statements
    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")
        return []

def generate_bulk_output(file_paths, output_folder, chunk_size=100): #Change Chunk Size if you want
    all_inserts = []
    for path in file_paths:
        inserts = extract_rows_from_xml(path)
        all_inserts.extend(inserts)

    total_parts = math.ceil(len(all_inserts) / chunk_size)
    output_files = []

    for i in range(total_parts):
        part = all_inserts[i * chunk_size:(i + 1) * chunk_size]
        file_path = os.path.join(output_folder, f"output_part_{i+1:03d}.sql")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("USE trickster_db;\nGO\n\n" + "\n\n".join(part))
        output_files.append(file_path)


    return output_files

def run_bulk_gui():
    root = Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="Select one or more XML files with <ROW> entries",
        filetypes=[("XML files", "*.xml")],
    )
    if not file_paths:
        messagebox.showinfo("Canceled", "No files selected.")
        return

    output_folder = filedialog.askdirectory(
        title="Choose output folder"
    )
    if not output_folder:
        messagebox.showinfo("Canceled", "No output folder selected.")
        return

    try:
        output_files = generate_bulk_output(file_paths, output_folder, chunk_size=100)
        if output_files:
            os.system(f'notepad "{output_files[0]}"')
            messagebox.showinfo("Done", f"{len(output_files)} SQL files created in:\n{output_folder}")
        else:
            messagebox.showwarning("No Inserts", "No valid <ROW> entries found in the selected files.")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

if __name__ == "__main__":
    run_bulk_gui()
