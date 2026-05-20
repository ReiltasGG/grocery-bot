import requests
import json

def get_groceries(meals):
    prompt = f"""You want to cook: {', '.join(meals)}.
Return ONLY a JSON object with this structure, no explanation, no markdown:
{{
  "meals": [
    {{
      "name": "meal name",
      "ingredients": ["ingredient 1 with amount", "ingredient 2 with amount"]
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


def combine_ingredients(meals_data):
    seen = {}
    for meal in meals_data:
        for ing in meal["ingredients"]:
            # use the ingredient name (lowercase) as the key to detect duplicates
            key = ing.strip().lower()
            if key not in seen:
                seen[key] = ing  # keep the original formatting
    return list(seen.values())


def main():
    print("=== Grocery List Tool ===\n")
    meals = []

    while True:
        meal = input("Enter a meal (or press Enter when done): ").strip()
        if not meal:
            break
        meals.append(meal)

    if not meals:
        print("No meals entered.")
        return

    print("\nThinking...\n")
    data = get_groceries(meals)

    # show ingredients per meal
    for meal in data["meals"]:
        print(f"[ {meal['name']} ]")
        for ing in meal["ingredients"]:
            print(f"  - {ing}")

    # combine and deduplicate
    all_ingredients = combine_ingredients(data["meals"])

    print("\n=== What do you already have? ===")
    have = []
    for ing in all_ingredients:
        answer = input(f"  Do you have {ing}? (y/n): ").strip().lower()
        if answer == "y":
            have.append(ing)

    need = [i for i in all_ingredients if i not in have]

    print("\n=== YOUR GROCERY LIST ===")
    for item in need:
        print(f"  [ ] {item}")

if __name__ == "__main__":
    main()