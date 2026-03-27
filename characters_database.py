#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
База знаний популярных персонажей для AI генерации изображений
"""

# База популярных персонажей
CHARACTERS = {
    # Valorant
    "jett": "Young athletic woman with short white hair, bright blue eyes, wearing blue and white tactical jacket with hood, black fingerless gloves, sporty build, confident smirk, wind effects swirling around her",
    "sage": "Elegant woman with long black hair in traditional Chinese bun, calm wise expression, wearing white and teal traditional Chinese-inspired outfit with jade ornaments, healing energy aura",
    "phoenix": "Confident man with blonde spiky hair, British style, wearing orange and black jacket with flame patterns, fiery personality, flame effects around hands",
    "reyna": "Mysterious woman with long purple hair, purple glowing eyes, wearing purple and black tactical outfit, soul orbs floating around her, vampiric aesthetic",
    
    # Genshin Impact
    "hu tao": "Playful girl with long brown hair in twin tails, red eyes, wearing traditional Chinese red and black outfit with ghost motifs, holding wooden staff, mischievous smile",
    "raiden": "Majestic woman with long purple hair in braid, purple glowing eyes, wearing purple and white kimono-style outfit, electro effects, katana sword",
    "ganyu": "Gentle girl with long blue hair with horns, wearing blue and white qipao dress, ice aesthetic, shy expression",
    
    # Anime
    "naruto": "Young ninja with spiky blonde hair, blue eyes, wearing orange and black jumpsuit, headband with leaf symbol, whisker marks on cheeks",
    "goku": "Muscular man with spiky black hair, orange gi uniform with blue undershirt, powerful aura",
    "nezuko": "Young girl with long black hair fading to orange, pink kimono with bamboo in mouth, demon features, cute appearance",
}

# Художественные стили
STYLES = {
    "realistic": "📸 Реализм|photorealistic, 8k uhd, professional photography, detailed textures, natural lighting",
    "anime": "🎭 Аниме|anime style, vibrant colors, cel shaded, detailed linework, manga aesthetic",
    "cyberpunk": "🌃 Киберпанк|cyberpunk style, neon lights, futuristic, dark atmosphere, rain-slicked streets",
    "fantasy": "🧙 Фэнтези|fantasy art style, magical atmosphere, ethereal lighting, epic composition",
    "cartoon": "🎨 Мультяшный|cartoon style, bold outlines, vibrant colors, Disney/Pixar quality",
    "oil": "🖼️ Масло|oil painting style, brushstroke textures, classical art, rich colors",
    "digital": "💻 Digital Art|digital art, modern illustration, clean lines, trending on artstation",
    "pixel": "🎮 Pixel Art|pixel art style, retro gaming, 16-bit graphics, nostalgic feel",
    "watercolor": "🌊 Акварель|watercolor painting, soft edges, flowing colors, artistic",
    "sketch": "✏️ Эскиз|pencil sketch, hand-drawn, artistic linework, shading",
    "3d": "🎲 3D Рендер|3D render, CGI, octane render, unreal engine, ray tracing",
    "comic": "📚 Комикс|comic book style, bold lines, halftone shading, Marvel/DC aesthetic"
}

# Настройки качества
QUALITY = {
    "fast": {"size": 512, "name": "⚡ Быстро", "time": "~5 сек"},
    "normal": {"size": 1024, "name": "⚙️ Обычно", "time": "~10 сек"},
    "high": {"size": 1024, "name": "💎 Высокое", "time": "~15 сек"}
}

