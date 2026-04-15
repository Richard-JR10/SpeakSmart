# scripts/phrase_data.py

MODULES = [
    {"module_id": "module_greetings", "title": "Greetings", "description": "Basic Japanese greetings for tourism contexts", "order_index": 1},
    {"module_id": "module_hotel", "title": "Hotel", "description": "Hotel check-in, requests, and service phrases", "order_index": 2},
    {"module_id": "module_directions", "title": "Directions", "description": "Giving and understanding directions", "order_index": 3},
    {"module_id": "module_food", "title": "Food & Dining", "description": "Restaurant and food service phrases", "order_index": 4},
    {"module_id": "module_emergency", "title": "Emergency", "description": "Emergency and safety phrases", "order_index": 5},
    {"module_id": "module_tour_guide", "title": "Tour Guide", "description": "Tour guide narration and visitor assistance", "order_index": 6},
]

PHRASES = [
    # --- Greetings ---
    {"phrase_id": "ph_greet_001", "module_id": "module_greetings", "japanese_text": "こんにちは", "romaji": "Konnichiwa", "english_translation": "Hello / Good afternoon", "difficulty_level": 1},
    {"phrase_id": "ph_greet_002", "module_id": "module_greetings", "japanese_text": "おはようございます", "romaji": "Ohayou gozaimasu", "english_translation": "Good morning", "difficulty_level": 1},
    {"phrase_id": "ph_greet_003", "module_id": "module_greetings", "japanese_text": "こんばんは", "romaji": "Konbanwa", "english_translation": "Good evening", "difficulty_level": 1},
    {"phrase_id": "ph_greet_004", "module_id": "module_greetings", "japanese_text": "はじめまして", "romaji": "Hajimemashite", "english_translation": "Nice to meet you", "difficulty_level": 2},
    {"phrase_id": "ph_greet_005", "module_id": "module_greetings", "japanese_text": "よろしくおねがいします", "romaji": "Yoroshiku onegaishimasu", "english_translation": "Please treat me well", "difficulty_level": 3},
    {"phrase_id": "ph_greet_006", "module_id": "module_greetings", "japanese_text": "ありがとうございます", "romaji": "Arigatou gozaimasu", "english_translation": "Thank you very much", "difficulty_level": 2},

    # --- Hotel ---
    {"phrase_id": "ph_hotel_001", "module_id": "module_hotel", "japanese_text": "チェックインをおねがいします", "romaji": "Chekkuin wo onegaishimasu", "english_translation": "I would like to check in", "difficulty_level": 2},
    {"phrase_id": "ph_hotel_002", "module_id": "module_hotel", "japanese_text": "よやくしています", "romaji": "Yoyaku shite imasu", "english_translation": "I have a reservation", "difficulty_level": 2},
    {"phrase_id": "ph_hotel_003", "module_id": "module_hotel", "japanese_text": "へやのかぎをなくしました", "romaji": "Heya no kagi wo nakushimashita", "english_translation": "I lost my room key", "difficulty_level": 3},
    {"phrase_id": "ph_hotel_004", "module_id": "module_hotel", "japanese_text": "タオルをもってきてください", "romaji": "Taoru wo motte kite kudasai", "english_translation": "Please bring towels", "difficulty_level": 3},
    {"phrase_id": "ph_hotel_005", "module_id": "module_hotel", "japanese_text": "チェックアウトはなんじですか", "romaji": "Chekkuauto wa nanji desu ka", "english_translation": "What time is check-out?", "difficulty_level": 2},
    {"phrase_id": "ph_hotel_006", "module_id": "module_hotel", "japanese_text": "WiFiのパスワードをおしえてください", "romaji": "WiFi no pasuwaado wo oshiete kudasai", "english_translation": "Please tell me the WiFi password", "difficulty_level": 3},

    # --- Directions ---
    {"phrase_id": "ph_dir_001", "module_id": "module_directions", "japanese_text": "えきはどこですか", "romaji": "Eki wa doko desu ka", "english_translation": "Where is the station?", "difficulty_level": 1},
    {"phrase_id": "ph_dir_002", "module_id": "module_directions", "japanese_text": "みぎにまがってください", "romaji": "Migi ni magatte kudasai", "english_translation": "Please turn right", "difficulty_level": 2},
    {"phrase_id": "ph_dir_003", "module_id": "module_directions", "japanese_text": "ひだりにまがってください", "romaji": "Hidari ni magatte kudasai", "english_translation": "Please turn left", "difficulty_level": 2},
    {"phrase_id": "ph_dir_004", "module_id": "module_directions", "japanese_text": "まっすぐいってください", "romaji": "Massugu itte kudasai", "english_translation": "Please go straight", "difficulty_level": 2},
    {"phrase_id": "ph_dir_005", "module_id": "module_directions", "japanese_text": "ここからとおいですか", "romaji": "Koko kara tooi desu ka", "english_translation": "Is it far from here?", "difficulty_level": 2},
    {"phrase_id": "ph_dir_006", "module_id": "module_directions", "japanese_text": "ちずをかいてもらえますか", "romaji": "Chizu wo kaite moraemasu ka", "english_translation": "Could you draw me a map?", "difficulty_level": 4},

    # --- Food ---
    {"phrase_id": "ph_food_001", "module_id": "module_food", "japanese_text": "メニューをみせてください", "romaji": "Menyuu wo misete kudasai", "english_translation": "Please show me the menu", "difficulty_level": 1},
    {"phrase_id": "ph_food_002", "module_id": "module_food", "japanese_text": "これをください", "romaji": "Kore wo kudasai", "english_translation": "I will have this please", "difficulty_level": 1},
    {"phrase_id": "ph_food_003", "module_id": "module_food", "japanese_text": "おすすめはなんですか", "romaji": "Osusume wa nan desu ka", "english_translation": "What do you recommend?", "difficulty_level": 2},
    {"phrase_id": "ph_food_004", "module_id": "module_food", "japanese_text": "アレルギーがあります", "romaji": "Arerugii ga arimasu", "english_translation": "I have allergies", "difficulty_level": 3},
    {"phrase_id": "ph_food_005", "module_id": "module_food", "japanese_text": "おかいけいをおねがいします", "romaji": "Okaikei wo onegaishimasu", "english_translation": "Check please", "difficulty_level": 2},
    {"phrase_id": "ph_food_006", "module_id": "module_food", "japanese_text": "とてもおいしかったです", "romaji": "Totemo oishikatta desu", "english_translation": "It was very delicious", "difficulty_level": 3},

    # --- Emergency ---
    {"phrase_id": "ph_emer_001", "module_id": "module_emergency", "japanese_text": "たすけてください", "romaji": "Tasukete kudasai", "english_translation": "Please help me", "difficulty_level": 1},
    {"phrase_id": "ph_emer_002", "module_id": "module_emergency", "japanese_text": "きゅうきゅうしゃをよんでください", "romaji": "Kyuukyuusha wo yonde kudasai", "english_translation": "Please call an ambulance", "difficulty_level": 3},
    {"phrase_id": "ph_emer_003", "module_id": "module_emergency", "japanese_text": "けいさつをよんでください", "romaji": "Keisatsu wo yonde kudasai", "english_translation": "Please call the police", "difficulty_level": 3},
    {"phrase_id": "ph_emer_004", "module_id": "module_emergency", "japanese_text": "ぐあいがわるいです", "romaji": "Guai ga warui desu", "english_translation": "I am not feeling well", "difficulty_level": 2},
    {"phrase_id": "ph_emer_005", "module_id": "module_emergency", "japanese_text": "びょういんはどこですか", "romaji": "Byouin wa doko desu ka", "english_translation": "Where is the hospital?", "difficulty_level": 2},
    {"phrase_id": "ph_emer_006", "module_id": "module_emergency", "japanese_text": "パスポートをなくしました", "romaji": "Pasupooto wo nakushimashita", "english_translation": "I lost my passport", "difficulty_level": 3},

    # --- Tour Guide ---
    {"phrase_id": "ph_tour_001", "module_id": "module_tour_guide", "japanese_text": "ようこそフィリピンへ", "romaji": "Youkoso Firipin e", "english_translation": "Welcome to the Philippines", "difficulty_level": 1},
    {"phrase_id": "ph_tour_002", "module_id": "module_tour_guide", "japanese_text": "こちらにあつまってください", "romaji": "Kochira ni atsumatte kudasai", "english_translation": "Please gather here", "difficulty_level": 2},
    {"phrase_id": "ph_tour_003", "module_id": "module_tour_guide", "japanese_text": "しゃしんをとってもいいですか", "romaji": "Shashin wo totte mo ii desu ka", "english_translation": "May I take a photo?", "difficulty_level": 3},
    {"phrase_id": "ph_tour_004", "module_id": "module_tour_guide", "japanese_text": "つぎはうみにいきます", "romaji": "Tsugi wa umi ni ikimasu", "english_translation": "Next we will go to the sea", "difficulty_level": 2},
    {"phrase_id": "ph_tour_005", "module_id": "module_tour_guide", "japanese_text": "ここはゆうめいなかんこうちです", "romaji": "Koko wa yuumei na kankouchi desu", "english_translation": "This is a famous tourist spot", "difficulty_level": 3},
    {"phrase_id": "ph_tour_006", "module_id": "module_tour_guide", "japanese_text": "なにかしつもんはありますか", "romaji": "Nanika shitsumon wa arimasu ka", "english_translation": "Do you have any questions?", "difficulty_level": 3},
]