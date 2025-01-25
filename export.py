import os
import re
import sqlite3
import argparse


def convert_wikidpad_formatting_to_markdown(formatting, prefix):
    lines = formatting.split("\n")
    prefix_str = ""
    if prefix:
        prefix_str = prefix + "/"

    table_mode = False

    new_lines = []
    for l in lines:
        # Remove the unsupported centering
        l = l.replace("<center>", "").replace("</center>", "")
        l = re.sub("\[([^]]*)]", "[[" + prefix_str + "\\1]]", l)
        l = re.sub("rel://([^ ]*)", "![](../assets/\\1)", l)

        # Convert titles to markdown titles
        if l.startswith("++ "):
            new_lines.append(l.replace("++ ", "## "))

        # Turn on "table" mode and add the markdown table prefixes for the next rows
        elif l.startswith("<<|"):
            new_lines.append(l.replace("<<|", ""))
            table_mode = True

        # Turn off "table" mode
        elif l.startswith(">>"):
            new_lines.append(l.replace(">>", ""))
            table_mode = False

        else:
            # For table mode we need to add extra | at the start and end of it
            if table_mode:
                l = "| " + l + " |"

            new_lines.append(l)

    return "\n".join(new_lines)

def read_database(database, output_folder, prefix):
    print("Loading database...", database)
    print("Saving to output folder...", output_folder)
    if prefix is not None:
        print("Files will be prefixed by", prefix)


    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("select * from wikiwordcontent")
    for content in cur.fetchall():
        print("Processing file:", content['word'])

        if prefix:
            file_path = os.path.join(output_folder, prefix + "___" + content['word'] + ".md")
        else:
            file_path = os.path.join(output_folder, content['word'] + ".md")

        with open(file_path, "w") as f:
            f.write(convert_wikidpad_formatting_to_markdown(content['content'].decode("utf8"), prefix))

        print("Written file")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Wikidpad Exporter',
        description='Exports from Wikidpad into Markdown')

    parser.add_argument('database_file', help="Path to the wiki.sli file")
    parser.add_argument('output_folder', help="Path to the output folder")
    parser.add_argument('--prefix', required=False, default=None, help="Pages to export")

    args = parser.parse_args()

    read_database(args.database_file, args.output_folder, args.prefix)
