# grocery-bot 🛒

A terminal-based grocery list tool powered by **Gemma 4** running locally via **Ollama**. Enter the meals you want to cook and it generates a combined shopping list of ingredients — no internet required, everything runs on your machine.

## Requirements

- Python 3
- [Ollama](https://ollama.com) with `gemma4:e4b` installed
- `requests` Python library

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/ReiltasGG/grocery-bot.git
cd grocery-bot
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install requests
```

**4. Make sure Ollama is running**
```bash
ollama serve
```

## Usage

```bash
python grocery.py
```

- Enter as many meals as you want one by one
- Press **Enter** on a blank line when you're done
- The tool will generate all the ingredients needed
- Check off what you already have at home
- Get a clean grocery list of only what you need to buy

## Example

```
=== Grocery List Tool ===

Enter a meal (or press Enter when done): chicken stir fry
Enter a meal (or press Enter when done): pasta carbonara
Enter a meal (or press Enter when done):

Thinking...

[ chicken stir fry ]
  - 2 chicken breasts
  - 2 tbsp soy sauce
  - 1 tbsp sesame oil

[ pasta carbonara ]
  - 200g pasta
  - 3 egg yolks
  - 100g pancetta

=== What do you already have? ===
  Do you have 2 chicken breasts? (y/n): y
  ...

=== YOUR GROCERY LIST ===
  [ ] 2 tbsp soy sauce
  [ ] 1 tbsp sesame oil
  [ ] 200g pasta
  [ ] 3 egg yolks
  [ ] 100g pancetta
```

## Notes

- Duplicate ingredients across meals are automatically combined into one list
- Requires Ollama to be running locally before executing the script
- Model used: `gemma4:e4b`