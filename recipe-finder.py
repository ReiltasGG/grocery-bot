import requests
import json
import os
from datetime import datetime

def get_recipes(ingredients):
    prompt = f"""I have these ingredients: {', '.join(ingredients)}.

Suggest 1-3 recipes I can make. For each recipe, list the ingredients needed and flag any I might be missing from my list.

Return ONLY a JSON object, no explanation, no markdown:
{{
  "recipes": [
    {{
      "name": "recipe name",
      "ingredients_needed": ["ingredient 1", "ingredient 2"],
      "missing_ingredients": ["ingredient I dont have"],
      "description": "one sentence description"
    }}
  ]
}}"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma4:e4b",
        "prompt": prompt,
        "stream": False
    })

    raw = response.json()["response"]
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def get_steps(recipe_name, ingredients_needed):
    prompt = f"""Give me detailed step-by-step cooking instructions for {recipe_name}.
Ingredients available: {', '.join(ingredients_needed)}.

Return ONLY a JSON object, no explanation, no markdown:
{{
  "steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ]
}}"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma4:e4b",
        "prompt": prompt,
        "stream": False
    })

    raw = response.json()["response"]
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def save_to_file(recipe_name, ingredients_needed, missing, steps):
    # create a clean filename using the recipe name and current date/time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{recipe_name.replace(' ', '_')}_{timestamp}.txt"
    filepath = os.path.join(os.path.dirname(__file__), filename)

    with open(filepath, "w") as f:
        f.write(f"RECIPE: {recipe_name}\n")
        f.write(f"Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n")
        f.write("=" * 40 + "\n\n")

        f.write("INGREDIENTS USED:\n")
        for ing in ingredients_needed:
            f.write(f"  - {ing}\n")

        if missing:
            f.write("\nMISSING INGREDIENTS:\n")
            for ing in missing:
                f.write(f"  - {ing}\n")

        f.write("\nSTEPS:\n")
        for step in steps:
            f.write(f"  {step}\n")

    return filename


def main():
    print("=== Recipe Finder ===\n")
    ingredients = []

    while True:
        item = input("Enter an ingredient you have (or press Enter when done): ").strip()
        if not item:
            break
        ingredients.append(item)

    if not ingredients:
        print("No ingredients entered.")
        return

    print("\nFinding recipes...\n")
    data = get_recipes(ingredients)
    recipes = data["recipes"]

    # show recipe options
    print("Here's what you can make:\n")
    for i, recipe in enumerate(recipes, 1):
        print(f"  [{i}] {recipe['name']}")
        print(f"      {recipe['description']}")
        if recipe["missing_ingredients"]:
            print(f"      ⚠️  Missing: {', '.join(recipe['missing_ingredients'])}")
        else:
            print(f"      ✅ You have everything!")
        print()

    # ask user to pick one
    while True:
        choice = input(f"Which recipe do you want to make? (1-{len(recipes)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(recipes):
            break
        print(f"Please enter a number between 1 and {len(recipes)}")

    selected = recipes[int(choice) - 1]
    print(f"\nYou selected: {selected['name']}")

    # warn about missing ingredients
    if selected["missing_ingredients"]:
        print(f"\n⚠️  You are missing: {', '.join(selected['missing_ingredients'])}")
        input("Press Enter to continue anyway and get the recipe steps... ")
    else:
        print("\n✅ You have all the ingredients!")
        input("Press Enter to get the cooking steps... ")

    # get cooking steps
    print("\nGetting cooking instructions...\n")
    steps_data = get_steps(selected["name"], selected["ingredients_needed"])
    steps = steps_data["steps"]

    print(f"=== HOW TO MAKE {selected['name'].upper()} ===\n")
    for step in steps:
        print(f"  {step}")

    # save to file
    filename = save_to_file(
        selected["name"],
        selected["ingredients_needed"],
        selected["missing_ingredients"],
        steps
    )

    print(f"\n✅ Recipe saved to: {filename}")


if __name__ == "__main__":
    main()