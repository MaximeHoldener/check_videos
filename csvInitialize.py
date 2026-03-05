from xml.sax.saxutils import escape
import csv

# filenames
infil = "abonnements.csv"

# files
inf = ""

# opml variables
otitle = ""
ochannelID = ""

# open file with handling
try:
  inf = open(infil, "r", encoding="utf8")
except ValueError:
  print("Input file error: " & ValueError)


# Create and initialize the CSV file
csv_filename = "output.csv"
with open(csv_filename, "w", newline='', encoding="utf8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Channel", "xmlUrl", "LastVideo", "LastUrl"])
    # now process file, stripping needed info and write in csv file.
    for x in inf:
        infile = x.strip()
        if not "Channel Id" in infile and infile:
            work = infile.split(",")
            if len(work) == 3:
                ochannelID = work[0]
                otitle = escape(work[2])
                xml_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ochannelID}"
                # LastVideo and LastUrl can be filled later or left blank
                writer.writerow([otitle, xml_url, "", ""])

# close files
inf.close()
csvfile.close()





