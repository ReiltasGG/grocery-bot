# grocery-bot

A collection of locally-run AI-powered kitchen tools built with Python, Ollama, and Gemma 4. No subscriptions, no cloud — everything runs on your machine.

This project started as a simple grocery list generator and evolved into a full recipe finder with real recipe data, pantry memory, and PDF exports.

---

## Tools

### 1. `grocery.py` — Grocery List Generator
Enter the meals you want to cook and the tool figures out all the ingredients you need. Check off what you already have and get a clean shopping list of only what to buy.

**Features:**
- Enter multiple meals at once
- Powered by Gemma 4 running locally via Ollama
- Automatically deduplicates shared ingredients across meals
- Terminal-based, no internet required

---

### 2. `recipe_finder.py` — Recipe Finder V1
The reverse of the grocery tool. Enter what you have in your fridge and pantry and Gemma 4 suggests up to 3 recipes you can make. Pick one and get full step-by-step cooking instructions. Saves a `.txt` file of the recipe when you're done.

**Features:**
- Enter ingredients one by one
- Gemma 4 suggests 1-3 recipes based on what you have
- Flags any missing ingredients per recipe
- Full cooking instructions for your chosen recipe
- Saves a timestamped `.txt` file with ingredients and steps

---

### 3. `recipe_finder_v2.py` — Recipe Finder V2
A major upgrade to V1. Swaps Gemma 4 recipe knowledge for real verified recipes from TheMealDB API. Adds pantry memory so your ingredients are saved between sessions. Adds cuisine filtering so you can search by what you're craving. Exports a clean PDF with the meal image, ingredients, and steps.

**Features:**
- Pantry saved to `pantry.txt` — just update what's changed each session
- Cuisine craving filter (Mexican, Italian, Asian, Indian, French, Thai, Spanish, and more)
- Real recipes from [TheMealDB](https://www.themealdb.com) — no hallucinations
- Recipes sorted by fewest missing ingredients
- Flags exactly what you need to buy
- Exports a formatted PDF with meal photo, ingredients, and step-by-step instructions

---

## Evolution

| Feature | grocery.py | recipe_finder.py | recipe_finder_v2.py |
|---|---|---|---|
| AI Model | Gemma 4 (Ollama) | Gemma 4 (Ollama) | TheMealDB API |
| Direction | Meals → Ingredients | Ingredients → Recipes | Ingredients → Recipes |
| Pantry Memory | ❌ | ❌ | ✅ |
| Cuisine Filter | ❌ | ❌ | ✅ |
| Missing Ingredient Detection | ❌ | ✅ | ✅ |
| Output | Terminal | .txt file | PDF with image |
| Internet Required | ❌ | ❌ | ✅ (TheMealDB) |

---

## Setup

**Requirements:**
- Python 3
- [Ollama](https://ollama.com) with `gemma4:e4b` installed (required for `grocery.py` and `recipe_finder.py`)
- Internet connection (required for `recipe_finder_v2.py`)

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
pip install requests reportlab pillow
```

**4. Start Ollama (required for grocery.py and recipe_finder.py)**
```bash
ollama serve
```

---

## Usage

**Grocery List Generator:**
```bash
python grocery.py
```

**Recipe Finder V1:**
```bash
python recipe_finder.py
```

**Recipe Finder V2:**
```bash
python recipe_finder_v2.py
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| Ollama | Local LLM runtime |
| Gemma 4 | AI model for grocery.py and recipe_finder.py |
| TheMealDB API | Real recipe data for recipe_finder_v2.py |
| reportlab | PDF generation |
| Pillow | Image processing for PDF |
| requests | HTTP requests |

---

## Project Structure

```
grocery-bot/
├── grocery.py              # Grocery list generator
├── recipe_finder.py        # Recipe finder V1
├── recipe_finder_v2.py     # Recipe finder V2
├── pantry.txt              # Your saved pantry (auto-generated, not tracked by git)
├── .gitignore
└── README.md
```

---

*Built on a Mac with an Apple M1 Pro using Python, Ollama, and Gemma 4 running fully locally.*