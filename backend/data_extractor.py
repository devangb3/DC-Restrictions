import os
import csv
import json
from bs4 import BeautifulSoup

# Set the input and output file names
html_filename = "backend/Tercero.html"
csv_filename = "backend/menu.csv"

# Read the HTML file
with open(html_filename, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Prepare a list to hold our rows
rows = []

# The HTML file uses a tabbed interface where each day’s menu is in a div with an id like "tabXcontent".
# Find the container that holds all day tabs (usually within a div with id="tabs")
tabs_container = soup.find("div", id="tabs")
if not tabs_container:
    print("No tabs container found.")
    exit(1)

# Iterate over each day container (child div with id matching tab*content)
day_containers = tabs_container.find_all("div", id=lambda x: x and x.startswith("tab") and x.endswith("content"))
for day_div in day_containers:
    # Extract the day from the h3 tag (e.g., "Monday, March 31, 2025")
    h3 = day_div.find("h3")
    if not h3:
        continue
    day_text = h3.get_text(strip=True)
    
    # Within the day container, find meal sections.
    # We assume meal times are marked with h4 tags and only consider Breakfast, Lunch, or Dinner.
    meal_headers = day_div.find_all("h4")
    for meal_header in meal_headers:
        meal_time = meal_header.get_text(strip=True)
        # Only process if meal_time is one of the expected values
        if meal_time.lower() not in ["breakfast", "lunch", "dinner"]:
            continue

        # Initialize a dictionary to store recipes for this meal time.
        recipe_dict = {}

        # We need to collect recipes that appear after this h4 until the next h4.
        # Using next siblings:
        for sibling in meal_header.find_all_next():
            # Stop if we hit another h4 (new meal section) or an h3 (new day)
            if sibling.name in ["h4", "h3"]:
                break
            # Look for list items (li) with class 'trigger' which indicate a recipe.
            if sibling.name == "li" and 'trigger' in sibling.get("class", []):
                # Get the recipe name from the <span> inside the li.
                span = sibling.find("span")
                if not span:
                    continue
                recipe_name = span.get_text(strip=True)
                
                # Find the ingredients inside this recipe li.
                # We look for an <h6> tag with text "Ingredients" and get the next <p> tag.
                ingredients = ""
                h6_tags = sibling.find_all("h6")
                for h6 in h6_tags:
                    if h6.get_text(strip=True).lower() == "ingredients":
                        p = h6.find_next("p")
                        if p:
                            ingredients = p.get_text(strip=True)
                        break
                # Save recipe if ingredients were found (or leave ingredients blank if not)
                recipe_dict[recipe_name] = ingredients

        # If we found recipes for this meal section, add a row
        if recipe_dict:
            rows.append({
                "Day": day_text,
                "Meal Time": meal_time,
                "Recipe Dict": json.dumps(recipe_dict)  # store dictionary as a JSON string
            })

# Write the output to CSV. If the CSV file does not exist, it will be created.
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Day", "Meal Time", "Recipe Dict"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print(f"Data extraction complete. CSV file saved as '{csv_filename}'.")
