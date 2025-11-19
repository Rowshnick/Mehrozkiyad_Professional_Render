def generate_text(name, goal, chart):
    en = f"Short advisory for {name} about {goal}. Sun: {chart.get('sun')}, Moon: {chart.get('moon')}"
    fa = f"توصیه‌ای کوتاه برای {name} دربارهٔ {goal}. خورشید: {chart.get('sun')}, ماه: {chart.get('moon')}"
    return {'en':en,'fa':fa}
