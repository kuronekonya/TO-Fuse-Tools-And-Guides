import os

# === CONFIG ===
SOURCE_FOLDER = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(SOURCE_FOLDER, 'output_batches')
FILES_PER_BATCH = 20       # Or tweak this depending on how big each file is
MAX_CHARS_PER_BATCH = 1_000_000  # Optional limit on batch size (e.g., 1MB)

def combine_sql_files():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    sql_files = sorted(f for f in os.listdir(SOURCE_FOLDER) if f.endswith('.sql'))
    batch_num = 1
    file_counter = 0
    char_count = 0
    batch_lines = []

    for file in sql_files:
        path = os.path.join(SOURCE_FOLDER, file)
        with open(path, 'r', encoding='utf-8') as f:
            sql = f.read()
            if (file_counter >= FILES_PER_BATCH) or (char_count + len(sql) > MAX_CHARS_PER_BATCH):
                # Write current batch
                write_batch(batch_num, batch_lines)
                batch_num += 1
                file_counter = 0
                char_count = 0
                batch_lines = []

            batch_lines.append(f"-- FILE: {file}\n{sql.strip()}\n")
            file_counter += 1
            char_count += len(sql)

    if batch_lines:
        write_batch(batch_num, batch_lines)

    print(f"✅ Finished batching into {batch_num} file(s). Saved in: {OUTPUT_FOLDER}")

def write_batch(batch_number, lines):
    batch_path = os.path.join(OUTPUT_FOLDER, f'batch_{batch_number:03}.sql')
    with open(batch_path, 'w', encoding='utf-8') as out:
        out.write("\n\n".join(lines))

if __name__ == '__main__':
    combine_sql_files()
