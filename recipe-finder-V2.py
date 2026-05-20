import requests
import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib import colors
from PIL import Image as PILImage
import io

# ── pantry helpers ──────────────────────────────────────────────
PANTRY_FILE = os.path.join(os.path.dirname(__file__), "pantry.txt")

def load_pantry():
    if not os.path.exists(PANTRY_FILE):
        return []
    with open(PANTRY_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_pantry(ingredients):
    with open(PANTRY_FILE, "w") as f:
        for ing in ingredients:
            f.write(ing + "\n")

def update_pantry(existing):
    print("\nYour current pantry:")
    if existing:
        for i, ing in enumerate(existing, 1):
            print(f"  {i}. {ing}")
    else:
        print("  (empty)")

    print("\nWhat's changed? (press Enter to skip a section)")

    # add new items
    new_items = []
    print("\nAdd new ingredients (comma separated, or press Enter to skip):")
    raw = input("  > ").strip()
    if raw:
        new_items = [i.strip() for i in raw.split(",") if i.strip()]

    # remove items
    remove_items = []
    if existing:
        print("\nAnything you've run out of? (comma separated, or press Enter to skip):")
        raw = input("  > ").strip()
        if raw:
            remove_items = [i.strip().lower() for i in raw.split(",") if i.strip()]

    updated = [i for i in existing if i.lower() not in remove_items]
    updated += new_items
    save_pantry(updated)
    return updated

# ── TheMealDB helpers ───────────────────────────────────────────
CUISINE_MAP = {
    "american": "American",
    "mexican": "Mexican",
    "italian": "Italian",
    "asian": "Chinese",
    "japanese": "Japanese",
    "indian": "Indian",
    "french": "French",
    "mediterranean": "Greek",
    "thai": "Thai",
    "spanish": "Spanish",
}

def search_by_ingredient(ingredient):
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    resp = requests.get(url)
    data = resp.json()
    return data.get("meals") or []

def search_by_cuisine(cuisine):
    area = CUISINE_MAP.get(cuisine.lower(), cuisine.capitalize())
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?a={area}"
    resp = requests.get(url)
    data = resp.json()
    return data.get("meals") or []

def get_meal_details(meal_id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    resp = requests.get(url)
    data = resp.json()
    meals = data.get("meals")
    return meals[0] if meals else None

def extract_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "").strip()
        measure = meal.get(f"strMeasure{i}", "").strip()
        if ing:
            ingredients.append(f"{measure} {ing}".strip())
    return ingredients

def find_recipes(pantry, cuisine=None):
    # search by first few proteins/main ingredients
    candidate_ids = set()

    # search by up to 3 ingredients to keep it fast
    search_ingredients = pantry[:3]
    for ing in search_ingredients:
        meals = search_by_ingredient(ing)
        for m in meals:
            candidate_ids.add(m["idMeal"])

    # if cuisine selected, intersect with cuisine results
    if cuisine:
        cuisine_meals = search_by_cuisine(cuisine)
        cuisine_ids = {m["idMeal"] for m in cuisine_meals}
        candidate_ids = candidate_ids & cuisine_ids

        # if intersection is empty, fall back to cuisine only
        if not candidate_ids:
            candidate_ids = cuisine_ids

    if not candidate_ids:
        return []

    # get details for up to 3 meals
    results = []
    for meal_id in list(candidate_ids)[:6]:
        detail = get_meal_details(meal_id)
        if detail:
            needed = extract_ingredients(detail)
            pantry_lower = [p.lower() for p in pantry]
            missing = [
                ing for ing in needed
                if not any(p in ing.lower() for p in pantry_lower)
            ]
            results.append({
                "name": detail["strMeal"],
                "id": meal_id,
                "description": detail.get("strCategory", ""),
                "ingredients_needed": needed,
                "missing_ingredients": missing,
                "steps": detail.get("strInstructions", ""),
                "image_url": detail.get("strMealThumb", "")
            })

    # sort by fewest missing ingredients
    results.sort(key=lambda x: len(x["missing_ingredients"]))
    return results[:3]

# ── PDF export ──────────────────────────────────────────────────
def save_to_pdf(recipe):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{recipe['name'].replace(' ', '_')}_{timestamp}.pdf"
    filepath = os.path.join(os.path.dirname(__file__), filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", fontSize=22, fontName="Helvetica-Bold",
                                  spaceAfter=6, textColor=colors.HexColor("#2C2C2C"))
    subtitle_style = ParagraphStyle("subtitle", fontSize=12, fontName="Helvetica",
                                     spaceAfter=12, textColor=colors.HexColor("#888888"))
    heading_style = ParagraphStyle("heading", fontSize=13, fontName="Helvetica-Bold",
                                    spaceAfter=6, spaceBefore=14,
                                    textColor=colors.HexColor("#444444"))
    body_style = ParagraphStyle("body", fontSize=11, fontName="Helvetica",
                                 spaceAfter=4, leading=16)

    story = []

    # title
    story.append(Paragraph(recipe["name"], title_style))
    story.append(Paragraph(f"Category: {recipe['description']}", subtitle_style))
    story.append(Spacer(1, 0.1 * inch))

    # meal image
    if recipe.get("image_url"):
        try:
            img_resp = requests.get(recipe["image_url"], timeout=5)
            img_data = PILImage.open(io.BytesIO(img_resp.content))
            img_buffer = io.BytesIO()
            img_data.save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            img = Image(img_buffer, width=4 * inch, height=3 * inch)
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
        except:
            pass

    # ingredients
    story.append(Paragraph("Ingredients", heading_style))
    for ing in recipe["ingredients_needed"]:
        story.append(Paragraph(f"• {ing}", body_style))

    # missing
    if recipe["missing_ingredients"]:
        story.append(Paragraph("Missing Ingredients", heading_style))
        for ing in recipe["missing_ingredients"]:
            story.append(Paragraph(f"• {ing}", body_style))

    # steps
    story.append(Paragraph("Instructions", heading_style))
    steps = recipe["steps"].replace("\r\n", "\n").split("\n")
    for step in steps:
        step = step.strip()
        if step:
            story.append(Paragraph(step, body_style))

    # footer
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y')} | TheMealDB",
        ParagraphStyle("footer", fontSize=9, textColor=colors.grey)
    ))

    doc.build(story)
    return filename

# ── main ─────────────────────────────────────────────────────────
def main():
    print("=== Recipe Finder V2 ===\n")

    # load and update pantry
    existing = load_pantry()
    pantry = update_pantry(existing)

    if not pantry:
        print("\nNo ingredients in pantry. Please add some first!")
        return

    # ask for cuisine craving
    print("\nAre you craving a specific cuisine?")
    print("Options: American, Mexican, Italian, Asian, Japanese, Indian, French, Thai, Spanish")
    cuisine = input("Enter cuisine or press Enter to skip: ").strip()

    print("\nSearching for recipes...\n")
    recipes = find_recipes(pantry, cuisine if cuisine else None)

    if not recipes:
        print("No recipes found. Try different ingredients or cuisine.")
        return

    # show options
    print("Here's what you can make:\n")
    for i, recipe in enumerate(recipes, 1):
        print(f"  [{i}] {recipe['name']} ({recipe['description']})")
        if recipe["missing_ingredients"]:
            print(f"      ⚠️  Missing: {', '.join(recipe['missing_ingredients'][:3])}")
        else:
            print(f"      ✅ You have everything!")
        print()

    # pick one
    while True:
        choice = input(f"Which recipe do you want to make? (1-{len(recipes)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(recipes):
            break
        print(f"Please enter a number between 1 and {len(recipes)}")

    selected = recipes[int(choice) - 1]
    print(f"\nYou selected: {selected['name']}")

    # missing ingredients warning
    if selected["missing_ingredients"]:
        print(f"\n⚠️  You are missing:")
        for ing in selected["missing_ingredients"]:
            print(f"  - {ing}")
        input("\nPress Enter to continue anyway and get the recipe steps... ")
    else:
        print("\n✅ You have all the ingredients!")
        input("Press Enter to get the cooking steps... ")

    # show steps
    print(f"\n=== HOW TO MAKE {selected['name'].upper()} ===\n")
    steps = selected["steps"].replace("\r\n", "\n").split("\n")
    for step in steps:
        step = step.strip()
        if step:
            print(f"  {step}\n")

    # save PDF
    print("Saving recipe as PDF...")
    filename = save_to_pdf(selected)
    print(f"\n✅ Recipe saved to: {filename}")

if __name__ == "__main__":
    main()