from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from config import Config

# Validate configuration
Config.validate()

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

app = FastAPI(title="Pandit Pradeep Kiradoo Astrology API", version="2.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq LLM (with fallback)
try:
    llm = ChatGroq(
        groq_api_key=Config.GROQ_API_KEY,
        model_name=Config.MODEL_NAME,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS
    )
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False
    print("⚠️ GROQ API not available, using fallback responses")

# Define the state structure
class AstrologyState:
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.problem_understood: bool = False
        self.remedies_provided: bool = False
        self.session_id: str = ""
        self.current_stage: str = "greeting"

# State management
sessions: Dict[str, AstrologyState] = {}

# Fallback responses for when GROQ is not available
FALLBACK_RESPONSES = {
    "greeting": [
        "**Namaste! 🙏** I am Pandit Pradeep Kiradoo, your Vedic astrology guide. Please tell me about the challenges or problems you're facing, and I'll provide astrological remedies based on planetary influences.",
        "**Welcome!** I am Pandit Pradeep Kiradoo, a Vedic astrologer with 15+ years of experience. How may I help you with your life's challenges today?",
        "**Jai Shree Ram! 🙏** I am Pandit Pradeep Kiradoo. Please share your concerns, and I'll guide you with Vedic wisdom and planetary remedies."
    ],
    "question_1": [
        "Thank you for sharing your concern. **How long have you been facing this issue?** Please tell me the duration - whether it's been days, weeks, months, or years.",
        "I understand you're going through difficulties. **When did this problem first start affecting you?** Knowing the timeline will help me provide better astrological guidance.",
        "Thank you for opening up. **How long has this been going on?** The duration of your challenge is important for understanding the planetary influences."
    ],
    "question_2": [
        "Thank you for that information. **How does this issue affect your daily life?** Does it impact your work, relationships, health, or other areas?",
        "I see. **In what ways does this problem impact your daily routine?** Understanding the effects will help me identify the specific planetary influences.",
        "Thank you. **How does this challenge affect your work, relationships, or health?** This helps me understand the scope of the problem."
    ],
    "question_3": [
        "I understand the impact. **What have you already tried to resolve this issue?** Have you attempted any solutions, remedies, or approaches?",
        "Thank you for sharing that. **What solutions have you attempted so far?** Knowing what you've tried helps me suggest different astrological remedies.",
        "I see. **What have you already tried to solve this problem?** This information helps me provide remedies that complement your efforts."
    ],
    "question_4": [
        "Thank you for that information. **How do you feel emotionally about this situation?** Are you feeling stressed, anxious, frustrated, or any other emotions?",
        "I understand. **What emotions do you experience because of this challenge?** Your emotional state is important for understanding the planetary influences.",
        "Thank you. **How do you feel about this situation emotionally?** Are you feeling overwhelmed, hopeful, or any other specific emotions?"
    ],
    "question_5": [
        "Thank you for sharing your feelings. **Are there any specific symptoms or manifestations you've noticed?** Any particular patterns or recurring issues?",
        "I understand your emotional state. **Can you describe any specific symptoms or patterns you've observed?** This helps me provide targeted remedies.",
        "Thank you. **What specific symptoms or manifestations have you noticed?** Any particular issues or patterns that stand out?"
    ],
    "analysis": [
        "**Based on Vedic Astrology Analysis** 🌟\n\nYour challenges appear to be related to planetary influences. Here are the recommended remedies:\n\n**1. Spiritual Practices**\n• Chant the **Gayatri Mantra** daily for spiritual strength\n• Perform **Surya Namaskar** (Sun Salutation) in the morning\n\n**2. Gemstone Recommendations**\n• Wear a **Blue Sapphire** (if Saturn is weak) or **Ruby** (if Sun is weak)\n\n**3. Donation & Charity**\n• Donate **yellow items** on Thursdays for Jupiter's blessings\n\n**4. Daily Rituals**\n• Light a **ghee lamp** in front of Lord Ganesha daily",
        "**Vedic Astrology Remedies** ✨\n\nAccording to planetary analysis, here are effective solutions:\n\n**1. Mantra & Prayer**\n• Recite **Hanuman Chalisa** daily for strength and courage\n• Perform **Rudrabhishek** for Shiva's blessings\n\n**2. Gemstone Therapy**\n• Wear a **Pearl** for Moon's positive influence\n\n**3. Charity & Donation**\n• Donate **white items** on Mondays\n\n**4. Meditation Practice**\n• Practice meditation during **Brahma Muhurat** (4-6 AM)",
        "**Planetary Pacification Remedies** 🙏\n\nVedic astrology indicates you need planetary pacification:\n\n**1. Mantra Chanting**\n• Chant **Om Namah Shivaya** 108 times daily\n\n**2. Gemstone Recommendations**\n• Wear an **Emerald** for Mercury's positive influence\n\n**3. Sacred Rituals**\n• Perform **Ganga Aarti** for purification\n\n**4. Charity Work**\n• Donate **green items** on Wednesdays\n\n**5. Energy Practices**\n• Practice **Pranayama** for energy balance"
    ],
    "ongoing": [
        "**Continue with these remedies regularly.** Remember, consistency is key in Vedic practices. Is there anything specific about these remedies you'd like me to explain further?",
        "**These remedies will bring positive changes gradually.** Stay patient and maintain faith. Would you like guidance on any other aspect of your life?",
        "**The remedies I've suggested are based on ancient Vedic wisdom.** Follow them with devotion and you'll see positive results. Do you have any other concerns?"
    ]
}

def get_fallback_response(stage: str, user_message: str = "", all_messages: List[Dict[str, Any]] = []) -> str:
    """Get a fallback response when GROQ is not available"""
    import random
    
    responses = FALLBACK_RESPONSES.get(stage, FALLBACK_RESPONSES["ongoing"])
    
    # For analysis stage, analyze all user answers to provide personalized remedies
    if stage == "analysis":
        # Extract user answers from the conversation
        user_answers = []
        for msg in all_messages:
            if msg["role"] == "user":
                user_answers.append(msg["content"].lower())
        
        # Analyze the problem type from the first answer
        problem_type = "general"
        if any(word in user_answers[0] for word in ["career", "job", "work", "business"]):
            problem_type = "career"
        elif any(word in user_answers[0] for word in ["relationship", "marriage", "love", "partner", "family"]):
            problem_type = "relationship"
        elif any(word in user_answers[0] for word in ["financial", "money", "wealth", "income", "debt"]):
            problem_type = "financial"
        elif any(word in user_answers[0] for word in ["health", "sick", "disease", "pain", "medical"]):
            problem_type = "health"
        
        # Analyze duration from answer 2
        duration = "medium"
        if len(user_answers) > 2:
            if any(word in user_answers[2] for word in ["days", "week", "recent"]):
                duration = "recent"
            elif any(word in user_answers[2] for word in ["months", "year", "long"]):
                duration = "long"
        
        # Analyze impact from answer 3
        impact = "general"
        if len(user_answers) > 3:
            if any(word in user_answers[3] for word in ["work", "job", "career"]):
                impact = "work"
            elif any(word in user_answers[3] for word in ["relationship", "family", "marriage"]):
                impact = "relationships"
            elif any(word in user_answers[3] for word in ["health", "sleep", "physical"]):
                impact = "health"
        
        # Analyze emotions from answer 5
        emotions = "stressed"
        if len(user_answers) > 5:
            if any(word in user_answers[5] for word in ["angry", "frustrated", "irritated"]):
                emotions = "angry"
            elif any(word in user_answers[5] for word in ["sad", "depressed", "hopeless"]):
                emotions = "sad"
            elif any(word in user_answers[5] for word in ["anxious", "worried", "fear"]):
                emotions = "anxious"
        
        # Generate personalized remedies based on analysis
        if problem_type == "career":
            if duration == "long" and impact == "work":
                return """**🕉️ Vedic Astrology Analysis - Career Challenges** 🌟

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Based on your detailed responses, I can see that you've been facing career challenges for an extended period. According to Vedic astrology, this indicates a weak **Surya (Sun)** and challenging **Shani (Saturn)** in your horoscope. The Sun represents leadership, authority, and career success, while Saturn brings delays and obstacles.

**🔮 Planetary Influences & Their Effects:**

**• Surya (Sun) - Currently Weak** 🌞
- **Effects**: Lack of leadership opportunities, low self-confidence, difficulty in decision-making
- **Career Impact**: Stagnation in promotions, lack of recognition, poor authority
- **Physical Symptoms**: Low energy, weak eyesight, heart-related issues

**• Shani (Saturn) - Creating Obstacles** 🪐
- **Effects**: Delays in projects, obstacles in career path, financial setbacks
- **Career Impact**: Job insecurity, conflicts with superiors, missed opportunities
- **Physical Symptoms**: Joint pain, skin problems, chronic health issues

**• Guru (Jupiter) - Needs Strengthening** 🪔
- **Effects**: Lack of wisdom, poor judgment, difficulty in learning
- **Career Impact**: Poor decision-making, lack of guidance, missed career opportunities
- **Physical Symptoms**: Weight gain, liver issues, diabetes risk

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Surya Upasana (Sun Worship) - Daily Practice** ☀️
• **Surya Namaskar**: Perform 12 rounds daily at sunrise facing east
• **Surya Mantra**: Chant *"Om Hraam Hreem Hraum Sah Suryaya Namah"* 108 times daily
• **Ruby Gemstone**: Wear a natural ruby ring on your ring finger on Sunday morning
• **Surya Arghya**: Offer water to the Sun daily at sunrise
• **Surya Puja**: Perform special Sun worship on Sundays
• **Red Items**: Wear red clothes on Sundays, donate red items

**2. Shani Shanti (Saturn Pacification) - Weekly Practice** 🪐
• **Shani Mantra**: Chant *"Om Sham Shanicharaya Namah"* 108 times on Saturdays
• **Shani Puja**: Perform special prayers to Lord Shani every Saturday
• **Sesame Oil Lamp**: Light a lamp with sesame oil on Saturdays
• **Black Items Donation**: Donate black clothes, blankets, or oil to the needy
• **Blue Sapphire**: Wear natural blue sapphire on Saturdays (consult astrologer first)
• **Shani Stotra**: Recite Shani Stotra daily

**3. Career-Specific Vedic Remedies** 💼
• **Gayatri Mantra**: Chant 108 times daily before starting work
• **Crystal Pyramid**: Keep a crystal pyramid on your work desk facing north
• **Guru Puja**: Worship Lord Jupiter on Thursdays with yellow items
• **Lakshmi Puja**: Perform Lakshmi puja on Fridays for prosperity
• **Career Yantra**: Install a career success yantra in your office
• **Money Plant**: Keep a money plant in your workspace

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For career success) - 21 times
• *"Om Namah Shivaya"* (For removing obstacles) - 108 times
• *"Om Gam Ganapataye Namah"* (For success in endeavors) - 21 times

**Evening Mantras (6:00 PM):**
• *"Om Hraam Hreem Hraum Sah Suryaya Namah"* (For Sun strength) - 108 times
• *"Om Sham Shanicharaya Namah"* (For Saturn pacification) - 108 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)
**• Surya Hora**: Sunrise time (Best for Sun-related remedies)
**• Guru Hora**: Thursday mornings (Best for Jupiter remedies)
**• Sandhya Kaal**: Dawn and dusk (Best for meditation)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Sundays: Fast for Sun strength
- Saturdays: Fast for Saturn pacification
- Thursdays: Fast for Jupiter blessings

**• Temple Visits:**
- Sundays: Visit Sun temples
- Tuesdays: Visit Hanuman temples
- Thursdays: Visit Jupiter temples
- Fridays: Visit Lakshmi temples

**• Charity & Donations:**
- Sundays: Donate jaggery, wheat, and red items
- Saturdays: Donate black clothes, blankets, oil
- Thursdays: Donate yellow items, books, sweets

**• Daily Rituals:**
- Light a ghee lamp in front of Lord Ganesha daily
- Keep a crystal pyramid on your work desk
- Practice meditation during Brahma Muhurat
- Recite Hanuman Chalisa daily

**📅 40-Day Remedy Schedule:**

**Week 1-2**: Focus on Sun remedies and basic practices
**Week 3-4**: Add Saturn pacification and advanced mantras
**Week 5-6**: Integrate all remedies and increase intensity

**✨ Divine Blessing:**

*May Lord Surya bless you with career success, may Shani's obstacles be removed from your path, and may Guru provide you with wisdom and guidance. Follow these remedies with faith and devotion for 40 days to see positive results.*

**Jai Shree Ram! 🙏**"""
            
            elif emotions == "anxious":
                return """**🕉️ Vedic Astrology Analysis - Career Anxiety** 🌙

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Your career anxiety indicates an afflicted **Chandra (Moon)** and weak **Budh (Mercury)** in your horoscope. The Moon governs the mind and emotions, while Mercury controls communication and intelligence. This combination creates mental restlessness and poor decision-making in career matters.

**🔮 Planetary Influences & Their Effects:**

**• Chandra (Moon) - Afflicted** 🌙
- **Effects**: Mental restlessness, anxiety, mood swings, lack of emotional stability
- **Career Impact**: Poor concentration, indecisiveness, emotional decision-making
- **Physical Symptoms**: Insomnia, digestive issues, water retention, eye problems

**• Budh (Mercury) - Weak** 🪔
- **Effects**: Poor communication, lack of clarity, difficulty in learning new skills
- **Career Impact**: Misunderstandings at work, poor presentation skills, missed opportunities
- **Physical Symptoms**: Nervous disorders, speech problems, skin issues

**• Mangal (Mars) - Needs Balancing** 🔴
- **Effects**: Lack of courage, low energy, poor confidence in career decisions
- **Career Impact**: Hesitation in taking risks, fear of failure, lack of assertiveness
- **Physical Symptoms**: Low blood pressure, anemia, lack of stamina

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Chandra Shanti (Moon Pacification) - Daily Practice** 🌙
• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday
• **Chandra Mantra**: Chant *"Om Shram Shreem Shraum Sah Chandramase Namah"* 108 times daily
• **White Items**: Donate white clothes, milk, or sweets on Mondays
• **Moon Meditation**: Meditate during full moon nights
• **Chandra Puja**: Perform special Moon worship on Mondays
• **Silver Items**: Wear silver ornaments on Mondays

**2. Budh Strengthening (Mercury Enhancement) - Weekly Practice** 🪔
• **Emerald Gemstone**: Wear a natural emerald ring on your little finger on Wednesday
• **Budh Mantra**: Chant *"Om Bram Breem Braum Sah Budhaya Namah"* 108 times on Wednesdays
• **Green Items**: Donate green clothes or vegetables on Wednesdays
• **Ganesha Puja**: Worship Lord Ganesha for intelligence
• **Budh Stotra**: Recite Budh Stotra daily
• **Green Crystal**: Keep green crystals on your work desk

**3. Mind Calming Remedies** 🧘‍♂️
• **Om Namah Shivaya**: Chant 108 times daily for peace
• **Pranayama**: Practice Sheetali and Nadi Shodhana breathing
• **Ghee Lamp**: Light a ghee lamp in front of Lord Shiva daily
• **Hanuman Chalisa**: Recite daily for courage and strength
• **Meditation**: Practice mindfulness meditation daily
• **Aromatherapy**: Use lavender and sandalwood oils

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Shram Shreem Shraum Sah Chandramase Namah"* (For Moon pacification) - 108 times
• *"Om Bram Breem Braum Sah Budhaya Namah"* (For Mercury strength) - 108 times
• *"Om Namah Shivaya"* (For peace) - 21 times

**Evening Mantras (6:00 PM):**
• *"Om Mani Padme Hum"* (For mental peace) - 108 times
• *"Om Shanti Shanti Shanti"* (For peace in all three worlds) - 21 times
• *"Om Aim Hreem Shreem Saraswatyai Namah"* (For wisdom) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)
**• Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)
**• Pradosh Kaal**: Evening twilight (Best for Shiva worship)
**• Chandra Hora**: Monday mornings (Best for Moon remedies)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Mondays: Fast for Moon pacification
- Wednesdays: Fast for Mercury strength
- Tuesdays: Fast for Mars balancing

**• Temple Visits:**
- Mondays: Visit Moon temples and Shiva temples
- Wednesdays: Visit Ganesha temples
- Tuesdays: Visit Hanuman temples

**• Charity & Donations:**
- Mondays: Donate white items, milk, sweets
- Wednesdays: Donate green items, books, pens
- Tuesdays: Donate red items for courage

**• Daily Rituals:**
- Practice deep breathing exercises
- Keep a white crystal on your desk
- Use calming essential oils
- Practice gratitude journaling

**📅 21-Day Remedy Schedule:**

**Week 1**: Focus on Moon pacification and basic meditation
**Week 2**: Add Mercury strengthening and advanced breathing
**Week 3**: Integrate all remedies and increase meditation time

**✨ Divine Blessing:**

*May Lord Chandra calm your mind, may Budh enhance your intelligence, and may Mangal provide you with courage and confidence. Follow these remedies with devotion for 21 days to experience mental peace and career clarity.*

**Jai Shree Ram! 🙏**"""
            
            else:
                return """**🕉️ Vedic Astrology Analysis - Career Guidance** 💼

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Your career situation indicates the need for strengthening **Surya (Sun)** and **Guru (Jupiter)** in your horoscope. These planets govern career success and professional growth. A balanced combination of these planetary energies will bring success, recognition, and professional advancement.

**🔮 Planetary Influences & Their Effects:**

**• Surya (Sun) - Needs Strengthening** 🌞
- **Effects**: Lack of leadership qualities, low self-esteem, poor authority
- **Career Impact**: Difficulty in getting promotions, lack of recognition, poor decision-making
- **Physical Symptoms**: Low energy, weak eyesight, heart-related issues

**• Guru (Jupiter) - Requires Enhancement** 🪔
- **Effects**: Lack of wisdom, poor judgment, difficulty in learning new skills
- **Career Impact**: Poor career choices, lack of guidance, missed opportunities
- **Physical Symptoms**: Weight gain, liver issues, diabetes risk

**• Shukra (Venus) - For Professional Skills** ✨
- **Effects**: Lack of charm, poor communication skills, difficulty in networking
- **Career Impact**: Poor presentation skills, difficulty in building relationships
- **Physical Symptoms**: Skin problems, eye issues, reproductive health

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Surya Upasana (Sun Worship) - Daily Practice** ☀️
• **Surya Namaskar**: Perform 12 rounds daily at sunrise facing east
• **Surya Mantra**: Chant *"Om Hraam Hreem Hraum Sah Suryaya Namah"* 108 times daily
• **Ruby Gemstone**: Wear a natural ruby ring on your ring finger on Sunday morning
• **Surya Arghya**: Offer water to the Sun daily at sunrise
• **Surya Puja**: Perform special Sun worship on Sundays
• **Red Items**: Wear red clothes on Sundays, donate red items

**2. Guru Puja (Jupiter Worship) - Weekly Practice** 🪔
• **Guru Mantra**: Chant *"Om Gram Greem Graum Sah Gurve Namah"* 108 times on Thursdays
• **Yellow Sapphire**: Wear a natural yellow sapphire ring on your index finger
• **Yellow Items**: Donate yellow clothes, books, or sweets on Thursdays
• **Guru Puja**: Worship Lord Jupiter on Thursdays
• **Guru Stotra**: Recite Guru Stotra daily
• **Yellow Crystal**: Keep yellow crystals on your work desk

**3. Professional Success Remedies** 💼
• **Lakshmi Puja**: Perform Lakshmi puja on Fridays for prosperity
• **Gayatri Mantra**: Chant 108 times daily for wisdom
• **Hanuman Chalisa**: Recite daily for strength and courage
• **Money Plant**: Keep a money plant in your office
• **Career Yantra**: Install a career success yantra
• **Crystal Pyramid**: Keep a crystal pyramid facing north

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Hraam Hreem Hraum Sah Suryaya Namah"* (For Sun strength) - 108 times
• *"Om Gram Greem Graum Sah Gurve Namah"* (For Jupiter wisdom) - 108 times
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For prosperity) - 21 times

**Evening Mantras (6:00 PM):**
• *"Om Namah Shivaya"* (For removing obstacles) - 108 times
• *"Om Gam Ganapataye Namah"* (For success) - 21 times
• *"Om Aim Hreem Shreem Saraswatyai Namah"* (For wisdom) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)
**• Surya Hora**: Sunrise time (Best for Sun remedies)
**• Guru Hora**: Thursday mornings (Best for Jupiter remedies)
**• Sandhya Kaal**: Dawn and dusk (Best for meditation)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Sundays: Fast for Sun strength
- Thursdays: Fast for Jupiter blessings
- Fridays: Fast for Venus strength

**• Temple Visits:**
- Sundays: Visit Sun temples
- Thursdays: Visit Jupiter temples
- Fridays: Visit Lakshmi temples
- Tuesdays: Visit Hanuman temples

**• Charity & Donations:**
- Sundays: Donate jaggery, wheat, red items
- Thursdays: Donate yellow items, books, sweets
- Fridays: Donate white sweets, flowers

**• Daily Rituals:**
- Light a ghee lamp in front of Lord Ganesha daily
- Keep a crystal pyramid on your work desk
- Practice meditation during Brahma Muhurat
- Recite Hanuman Chalisa daily

**📅 40-Day Remedy Schedule:**

**Week 1-2**: Focus on Sun remedies and basic practices
**Week 3-4**: Add Jupiter remedies and advanced mantras
**Week 5-6**: Integrate all remedies and increase intensity

**✨ Divine Blessing:**

*May Lord Surya bless you with career success, may Guru provide you with wisdom and guidance, and may Shukra enhance your professional skills. Follow these remedies with faith and devotion for 40 days.*

**Jai Shree Ram! 🙏**"""
        
        elif problem_type == "relationship":
            if emotions == "angry" and impact == "relationships":
                return """**🕉️ Vedic Astrology Analysis - Relationship Anger** 🔴

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Your anger affecting relationships indicates an afflicted **Mangal (Mars)** and weak **Shukra (Venus)** in your horoscope. Mars governs aggression and courage, while Venus controls love and relationships. This combination creates conflicts, misunderstandings, and emotional turmoil in your relationships.

**🔮 Planetary Influences & Their Effects:**

**• Mangal (Mars) - Afflicted** 🔴
- **Effects**: Excessive anger, aggression, impatience, lack of emotional control
- **Relationship Impact**: Frequent arguments, conflicts with partner, family disputes
- **Physical Symptoms**: High blood pressure, headaches, skin inflammations, anger-related stress

**• Shukra (Venus) - Weak** ✨
- **Effects**: Lack of love, poor harmony, difficulty in expressing affection
- **Relationship Impact**: Poor communication, lack of romance, emotional distance
- **Physical Symptoms**: Skin problems, eye issues, reproductive health issues

**• Chandra (Moon) - Needs Pacification** 🌙
- **Effects**: Emotional instability, mood swings, lack of empathy
- **Relationship Impact**: Poor emotional understanding, lack of patience
- **Physical Symptoms**: Insomnia, digestive issues, water retention

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Mangal Shanti (Mars Pacification) - Daily Practice** 🔴
• **Red Coral**: Wear a natural red coral ring on your ring finger on Tuesday
• **Mangal Mantra**: Chant *"Om Kram Kreem Kraum Sah Bhaumaya Namah"* 108 times daily
• **Red Items**: Donate red clothes, sweets, or items on Tuesdays
• **Hanuman Puja**: Worship Lord Hanuman on Tuesdays
• **Mangal Stotra**: Recite Mangal Stotra daily
• **Red Crystal**: Keep red crystals in your living space

**2. Shukra Strengthening (Venus Enhancement) - Weekly Practice** ✨
• **Pearl/Diamond**: Wear a natural pearl or diamond ring on your ring finger on Friday
• **Shukra Mantra**: Chant *"Om Dram Dreem Draum Sah Shukraya Namah"* 108 times on Fridays
• **Lakshmi Puja**: Perform Lakshmi puja on Fridays
• **White Items**: Donate white sweets or clothes on Fridays
• **Shukra Stotra**: Recite Shukra Stotra daily
• **Rose Quartz**: Keep rose quartz crystals for love

**3. Anger Management Remedies** 🧘‍♂️
• **Sheetali Pranayama**: Practice cooling breath for anger control
• **Om Namah Shivaya**: Chant 108 times daily for peace
• **Rose-scented Lamp**: Light a rose-scented lamp on Fridays
• **Loving-kindness Meditation**: Practice daily for compassion
• **Anger Journal**: Write down triggers and practice forgiveness
• **Cooling Foods**: Consume cooling foods like cucumber, mint

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Kram Kreem Kraum Sah Bhaumaya Namah"* (For Mars pacification) - 108 times
• *"Om Dram Dreem Draum Sah Shukraya Namah"* (For Venus strength) - 108 times
• *"Om Namah Shivaya"* (For peace) - 21 times

**Evening Mantras (6:00 PM):**
• *"Om Shanti Shanti Shanti"* (For peace in all three worlds) - 108 times
• *"Om Mani Padme Hum"* (For compassion) - 21 times
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For love) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)
**• Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)
**• Shukra Hora**: Friday mornings (Best for Venus remedies)
**• Mangal Hora**: Tuesday mornings (Best for Mars remedies)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Tuesdays: Fast for Mars pacification
- Fridays: Fast for Venus strength
- Mondays: Fast for Moon pacification

**• Temple Visits:**
- Tuesdays: Visit Hanuman temples
- Fridays: Visit Lakshmi temples
- Mondays: Visit Shiva temples

**• Charity & Donations:**
- Tuesdays: Donate red items, sweets
- Fridays: Donate white sweets, flowers
- Mondays: Donate white items, milk

**• Daily Rituals:**
- Practice deep breathing exercises
- Keep rose quartz crystals in your bedroom
- Use calming essential oils (lavender, rose)
- Practice gratitude journaling

**📅 21-Day Remedy Schedule:**

**Week 1**: Focus on Mars pacification and anger management
**Week 2**: Add Venus strengthening and love practices
**Week 3**: Integrate all remedies and increase meditation time

**✨ Divine Blessing:**

*May Lord Mangal control your anger, may Shukra bring love and harmony to your relationships, and may Chandra provide emotional balance. Follow these remedies with devotion for 21 days.*

**Jai Shree Ram! 🙏**"""
            
            elif duration == "long":
                return """**🕉️ Vedic Astrology Analysis - Long-term Relationship Issues** 💔

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Long-term relationship problems indicate severely weak **Shukra (Venus)** and afflicted **Chandra (Moon)** in your horoscope. These planets are crucial for love, harmony, and emotional balance. When these planets are weak for extended periods, they create deep-seated relationship issues that require intensive remedies.

**🔮 Planetary Influences & Their Effects:**

**• Shukra (Venus) - Severely Weak** ✨
- **Effects**: Complete lack of love, deep emotional wounds, relationship trauma
- **Relationship Impact**: Long-term conflicts, emotional distance, lack of intimacy
- **Physical Symptoms**: Chronic skin problems, reproductive health issues, eye problems

**• Chandra (Moon) - Afflicted** 🌙
- **Effects**: Severe emotional instability, deep depression, lack of empathy
- **Relationship Impact**: Poor emotional understanding, long-term misunderstandings
- **Physical Symptoms**: Chronic insomnia, digestive disorders, mental health issues

**• Guru (Jupiter) - Needs Strengthening** 🪔
- **Effects**: Lack of wisdom in relationships, poor judgment, difficulty in forgiveness
- **Relationship Impact**: Inability to resolve conflicts, poor communication skills
- **Physical Symptoms**: Weight gain, liver issues, chronic health problems

**🪔 Intensive Vedic Remedies (Upayas):**

**1. Shukra Strengthening (Venus Enhancement) - Daily Practice** ✨
• **Diamond/Pearl**: Wear a natural diamond or pearl ring on your ring finger on Friday
• **Shukra Mantra**: Chant *"Om Dram Dreem Draum Sah Shukraya Namah"* 108 times daily
• **Lakshmi Aarti**: Perform Lakshmi aarti daily
• **White Items**: Donate white sweets, clothes, or milk on Fridays
• **Shukra Stotra**: Recite Shukra Stotra daily
• **Rose Quartz**: Keep rose quartz crystals in your bedroom

**2. Chandra Shanti (Moon Pacification) - Daily Practice** 🌙
• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday
• **Chandra Mantra**: Chant *"Om Shram Shreem Shraum Sah Chandramase Namah"* 108 times on Mondays
• **White Items**: Donate white items on Mondays
• **Full Moon Meditation**: Meditate during full moon nights
• **Chandra Puja**: Perform special Moon worship on Mondays
• **Silver Items**: Wear silver ornaments on Mondays

**3. Relationship Revival Remedies** 💕
• **Krishna Puja**: Light a ghee lamp in front of Lord Krishna daily
• **Radha-Krishna Mantra**: Chant *"Om Radha Krishnaya Namah"* 108 times daily
• **Rudrabhishek**: Perform Rudrabhishek for Shiva's blessings
• **Couple Donation**: Donate to couples in need
• **Love Yantra**: Install a love harmony yantra in your home
• **Tulsi Plant**: Keep a Tulsi plant in your home

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Dram Dreem Draum Sah Shukraya Namah"* (For Venus strength) - 108 times
• *"Om Shram Shreem Shraum Sah Chandramase Namah"* (For Moon pacification) - 108 times
• *"Om Radha Krishnaya Namah"* (For divine love) - 108 times

**Evening Mantras (6:00 PM):**
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For love and harmony) - 108 times
• *"Om Shanti Shanti Shanti"* (For peace) - 21 times
• *"Om Namah Shivaya"* (For removing obstacles) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)
**• Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)
**• Purnima**: Full moon nights (Best for Moon remedies)
**• Shukra Hora**: Friday mornings (Best for Venus remedies)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Fridays: Fast for Venus strength
- Mondays: Fast for Moon pacification
- Thursdays: Fast for Jupiter wisdom

**• Temple Visits:**
- Fridays: Visit Lakshmi temples
- Mondays: Visit Shiva temples
- Thursdays: Visit Jupiter temples
- Daily: Visit Krishna temples

**• Charity & Donations:**
- Fridays: Donate white sweets, flowers, clothes
- Mondays: Donate white items, milk, sweets
- Thursdays: Donate yellow items, books

**• Daily Rituals:**
- Light a ghee lamp in front of Lord Krishna daily
- Keep rose quartz crystals in your bedroom
- Practice loving-kindness meditation
- Use rose and jasmine essential oils

**📅 40-Day Intensive Remedy Schedule:**

**Week 1-2**: Focus on Venus strengthening and basic love practices
**Week 3-4**: Add Moon pacification and emotional healing
**Week 5-6**: Integrate all remedies and increase intensity

**✨ Divine Blessing:**

*May Lord Shukra bless you with divine love, may Chandra bring emotional harmony to your relationships, and may Guru provide wisdom to heal and rebuild. Follow these remedies with devotion for 40 days.*

**Jai Shree Ram! 🙏**"""
            
            else:
                return """**🕉️ Vedic Astrology Analysis - Relationship Guidance** 💕

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Your relationship issues indicate the need for strengthening **Shukra (Venus)** and **Chandra (Moon)** in your horoscope. These planets govern love, harmony, and emotional balance. A balanced combination of these planetary energies will bring love, understanding, and harmony to your relationships.

**🔮 Planetary Influences & Their Effects:**

**• Shukra (Venus) - Needs Strengthening** ✨
- **Effects**: Lack of love, poor harmony, difficulty in expressing affection
- **Relationship Impact**: Poor communication, lack of romance, emotional distance
- **Physical Symptoms**: Skin problems, eye issues, reproductive health issues

**• Chandra (Moon) - Requires Pacification** 🌙
- **Effects**: Emotional instability, mood swings, lack of empathy
- **Relationship Impact**: Poor emotional understanding, lack of patience
- **Physical Symptoms**: Insomnia, digestive issues, water retention

**• Budh (Mercury) - For Communication** 🪔
- **Effects**: Poor communication skills, misunderstandings, lack of clarity
- **Relationship Impact**: Difficulty in expressing feelings, poor listening skills
- **Physical Symptoms**: Nervous disorders, speech problems, skin issues

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Shukra Strengthening (Venus Enhancement) - Weekly Practice** ✨
• **Pearl/Diamond**: Wear a natural pearl or diamond ring on your ring finger on Friday
• **Shukra Mantra**: Chant *"Om Dram Dreem Draum Sah Shukraya Namah"* 108 times on Fridays
• **Lakshmi Puja**: Perform Lakshmi puja on Fridays
• **White Sweets**: Donate white sweets on Fridays
• **Shukra Stotra**: Recite Shukra Stotra daily
• **Rose Quartz**: Keep rose quartz crystals for love

**2. Chandra Shanti (Moon Pacification) - Weekly Practice** 🌙
• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday
• **Chandra Mantra**: Chant *"Om Shram Shreem Shraum Sah Chandramase Namah"* 108 times on Mondays
• **White Items**: Donate white items on Mondays
• **Rose-scented Lamp**: Light a rose-scented lamp on Fridays
• **Chandra Puja**: Perform special Moon worship on Mondays
• **Silver Items**: Wear silver ornaments on Mondays

**3. Communication Enhancement** 💬
• **Emerald Gemstone**: Wear a natural emerald ring on your little finger on Wednesday
• **Budh Mantra**: Chant *"Om Bram Breem Braum Sah Budhaya Namah"* 108 times on Wednesdays
• **Ganesha Puja**: Worship Lord Ganesha for communication
• **Mindful Communication**: Practice daily
• **Budh Stotra**: Recite Budh Stotra daily
• **Green Crystal**: Keep green crystals for communication

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Dram Dreem Draum Sah Shukraya Namah"* (For Venus strength) - 108 times
• *"Om Shram Shreem Shraum Sah Chandramase Namah"* (For Moon pacification) - 108 times
• *"Om Bram Breem Braum Sah Budhaya Namah"* (For Mercury strength) - 108 times

**Evening Mantras (6:00 PM):**
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For love and harmony) - 108 times
• *"Om Shanti Shanti Shanti"* (For peace) - 21 times
• *"Om Gam Ganapataye Namah"* (For removing obstacles) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for meditation)
**• Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)
**• Shukra Hora**: Friday mornings (Best for Venus remedies)
**• Chandra Hora**: Monday mornings (Best for Moon remedies)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Fridays: Fast for Venus strength
- Mondays: Fast for Moon pacification
- Wednesdays: Fast for Mercury strength

**• Temple Visits:**
- Fridays: Visit Lakshmi temples
- Mondays: Visit Shiva temples
- Wednesdays: Visit Ganesha temples
- Daily: Visit Krishna temples

**• Charity & Donations:**
- Fridays: Donate white sweets, flowers, clothes
- Mondays: Donate white items, milk, sweets
- Wednesdays: Donate green items, books, pens

**• Daily Rituals:**
- Light a ghee lamp in front of Lord Krishna daily
- Keep rose quartz crystals in your bedroom
- Practice loving-kindness meditation
- Use rose and jasmine essential oils

**📅 21-Day Remedy Schedule:**

**Week 1**: Focus on Venus strengthening and basic love practices
**Week 2**: Add Moon pacification and emotional healing
**Week 3**: Integrate all remedies and increase meditation time

**✨ Divine Blessing:**

*May Lord Shukra bless you with love and harmony, may Chandra bring emotional balance to your relationships, and may Budh enhance your communication skills. Follow these remedies with faith for 21 days.*

**Jai Shree Ram! 🙏**"""
        
        elif problem_type == "financial":
            return """**🕉️ Vedic Astrology Analysis - Financial Guidance** 💰

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Your financial challenges indicate the need for strengthening **Guru (Jupiter)** and **Shukra (Venus)** in your horoscope. These planets govern wealth, prosperity, and material success. A balanced combination of these planetary energies will bring financial stability, abundance, and material prosperity.

**🔮 Planetary Influences & Their Effects:**

**• Guru (Jupiter) - Needs Strengthening** 🪔
- **Effects**: Lack of wisdom in financial decisions, poor investment choices, financial losses
- **Financial Impact**: Poor money management, debt accumulation, missed opportunities
- **Physical Symptoms**: Weight gain, liver issues, diabetes risk, financial stress

**• Shukra (Venus) - Requires Enhancement** ✨
- **Effects**: Lack of material desires, poor financial planning, difficulty in wealth accumulation
- **Financial Impact**: Poor business decisions, lack of financial growth, material dissatisfaction
- **Physical Symptoms**: Skin problems, eye issues, reproductive health issues

**• Kuber (Wealth God) - For Financial Stability** 🏦
- **Effects**: Financial instability, lack of savings, poor wealth preservation
- **Financial Impact**: Difficulty in maintaining wealth, poor financial security
- **Physical Symptoms**: Stress-related health issues, financial anxiety

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Guru Puja (Jupiter Worship) - Weekly Practice** 🪔
• **Yellow Sapphire**: Wear a natural yellow sapphire ring on your index finger on Thursday
• **Guru Mantra**: Chant *"Om Gram Greem Graum Sah Gurve Namah"* 108 times on Thursdays
• **Yellow Items**: Donate yellow clothes, books, or sweets on Thursdays
• **Guru Puja**: Worship Lord Jupiter on Thursdays
• **Guru Stotra**: Recite Guru Stotra daily
• **Yellow Crystal**: Keep yellow crystals for wealth

**2. Lakshmi Puja (Wealth Worship) - Daily Practice** 💰
• **Lakshmi Aarti**: Perform Lakshmi aarti daily
• **Lakshmi Mantra**: Chant *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* 108 times daily
• **Ghee Lamp**: Light a ghee lamp in front of Lakshmi daily
• **Money Plant**: Keep a money plant in your home
• **Lakshmi Yantra**: Install a Lakshmi yantra in your home
• **White Lotus**: Offer white lotus flowers to Lakshmi

**3. Kuber Puja (Wealth God Worship) - Weekly Practice** 🏦
• **Kuber Mantra**: Chant *"Om Yakshaya Kuberaya Vaishravanaya Dhanadhanyadi Padayeh Dhana-dhanya Samriddhi Me Dehi Tapaya Swaha"* daily
• **Kuber Puja**: Perform Kuber puja on Fridays
• **Temple Donation**: Donate to temples regularly
• **Charity**: Donate to the needy
• **Kuber Yantra**: Install a Kuber yantra in your home
• **Gold Items**: Keep gold items in your home

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For prosperity) - 108 times
• *"Om Gram Greem Graum Sah Gurve Namah"* (For Jupiter wisdom) - 108 times
• *"Om Kuberaya Namah"* (For wealth) - 21 times

**Evening Mantras (6:00 PM):**
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For daily prosperity) - 108 times
• *"Om Gam Ganapataye Namah"* (For success) - 21 times
• *"Om Namah Shivaya"* (For removing obstacles) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)
**• Guru Hora**: Thursday mornings (Best for Jupiter remedies)
**• Shukra Hora**: Friday mornings (Best for Venus remedies)
**• Sandhya Kaal**: Dawn and dusk (Best for meditation)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Thursdays: Fast for Jupiter blessings
- Fridays: Fast for Venus strength
- Saturdays: Fast for Saturn pacification

**• Temple Visits:**
- Thursdays: Visit Jupiter temples
- Fridays: Visit Lakshmi temples
- Saturdays: Visit Kuber temples
- Daily: Visit Hanuman temples

**• Charity & Donations:**
- Thursdays: Donate yellow items, books, sweets
- Fridays: Donate white sweets, flowers, clothes
- Saturdays: Donate black items, oil, blankets

**• Daily Rituals:**
- Light a ghee lamp in front of Lakshmi daily
- Keep a money plant in your home
- Practice gratitude for wealth
- Use prosperity essential oils (cinnamon, vanilla)

**📅 40-Day Remedy Schedule:**

**Week 1-2**: Focus on Jupiter remedies and basic wealth practices
**Week 3-4**: Add Lakshmi worship and prosperity mantras
**Week 5-6**: Integrate all remedies and increase intensity

**✨ Divine Blessing:**

*May Lord Guru bless you with wealth and wisdom, may Lakshmi bring prosperity to your life, and may Kuber ensure financial stability. Follow these remedies with devotion for 40 days.*

**Jai Shree Ram! 🙏**"""
        
        elif problem_type == "health":
            return """**🕉️ Vedic Astrology Analysis - Health Guidance** 🏥

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Your health concerns indicate the need for strengthening **Mangal (Mars)** and pacifying **Chandra (Moon)** in your horoscope. These planets govern physical health and mental well-being. A balanced combination of these planetary energies will bring physical vitality, mental peace, and overall wellness.

**🔮 Planetary Influences & Their Effects:**

**• Mangal (Mars) - Needs Strengthening** 🔴
- **Effects**: Lack of physical energy, poor immunity, low stamina, weak muscles
- **Health Impact**: Frequent illnesses, slow recovery, lack of physical strength
- **Physical Symptoms**: Anemia, low blood pressure, skin problems, joint pain

**• Chandra (Moon) - Requires Pacification** 🌙
- **Effects**: Mental restlessness, emotional instability, poor sleep, anxiety
- **Health Impact**: Stress-related illnesses, digestive problems, hormonal imbalances
- **Physical Symptoms**: Insomnia, water retention, digestive disorders, eye problems

**• Dhanvantari (Health God) - For Overall Wellness** 🏥
- **Effects**: Poor overall health, lack of healing energy, chronic health issues
- **Health Impact**: Difficulty in recovery, poor health maintenance
- **Physical Symptoms**: Chronic fatigue, weak immune system, poor vitality

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Mangal Strengthening (Mars Enhancement) - Daily Practice** 🔴
• **Red Coral**: Wear a natural red coral ring on your ring finger on Tuesday
• **Mangal Mantra**: Chant *"Om Kram Kreem Kraum Sah Bhaumaya Namah"* 108 times daily
• **Red Items**: Donate red clothes, sweets, or items on Tuesdays
• **Hanuman Puja**: Worship Lord Hanuman on Tuesdays
• **Mangal Stotra**: Recite Mangal Stotra daily
• **Red Crystal**: Keep red crystals for energy

**2. Chandra Shanti (Moon Pacification) - Daily Practice** 🌙
• **Pearl Gemstone**: Wear a natural pearl ring on your little finger on Monday
• **Chandra Mantra**: Chant *"Om Shram Shreem Shraum Sah Chandramase Namah"* 108 times on Mondays
• **White Items**: Donate white clothes, milk, or sweets on Mondays
• **Moon Meditation**: Meditate during full moon nights
• **Chandra Puja**: Perform special Moon worship on Mondays
• **Silver Items**: Wear silver ornaments on Mondays

**3. Health Enhancement Remedies** 🧘‍♂️
• **Om Namah Shivaya**: Chant 108 times daily for healing
• **Rudrabhishek**: Perform Rudrabhishek for Shiva's blessings
• **Dhanvantari Puja**: Worship Lord Dhanvantari for health
• **Yoga and Pranayama**: Practice daily for physical and mental health
• **Health Yantra**: Install a health yantra in your home
• **Healing Crystals**: Keep healing crystals in your bedroom

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Kram Kreem Kraum Sah Bhaumaya Namah"* (For Mars strength) - 108 times
• *"Om Shram Shreem Shraum Sah Chandramase Namah"* (For Moon pacification) - 108 times
• *"Om Namah Shivaya"* (For healing) - 21 times

**Evening Mantras (6:00 PM):**
• *"Om Dhanvantaraye Namah"* (For health) - 108 times
• *"Om Hanumate Rudraatmakaya Hum Phat"* (For strength) - 21 times
• *"Om Shanti Shanti Shanti"* (For peace) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for yoga and meditation)
**• Sandhya Kaal**: Dawn and dusk (Best for spiritual practices)
**• Mangal Hora**: Tuesday mornings (Best for Mars remedies)
**• Chandra Hora**: Monday mornings (Best for Moon remedies)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Tuesdays: Fast for Mars strength
- Mondays: Fast for Moon pacification
- Saturdays: Fast for Saturn pacification

**• Temple Visits:**
- Tuesdays: Visit Hanuman temples
- Mondays: Visit Shiva temples
- Saturdays: Visit Saturn temples
- Daily: Visit health temples

**• Charity & Donations:**
- Tuesdays: Donate red items, sweets
- Mondays: Donate white items, milk, sweets
- Saturdays: Donate black items, oil, blankets

**• Daily Rituals:**
- Practice Surya Namaskar daily
- Keep healing crystals in your bedroom
- Use healing essential oils (eucalyptus, tea tree)
- Practice gratitude for health

**📅 21-Day Remedy Schedule:**

**Week 1**: Focus on Mars strengthening and basic health practices
**Week 2**: Add Moon pacification and mental health practices
**Week 3**: Integrate all remedies and increase yoga time

**✨ Divine Blessing:**

*May Lord Mangal strengthen your physical health, may Chandra bring mental peace, and may Dhanvantari ensure overall wellness. Follow these remedies with devotion for 21 days.*

**Jai Shree Ram! 🙏**"""
        
        else:
            return """**🕉️ Vedic Astrology Analysis - Life Guidance** 🌟

*Om Namah Shivaya!* 🙏

**Pandit Pradeep Kiradoo's Jyotish Analysis:**

Your life challenges indicate the need for comprehensive planetary pacification and spiritual strengthening. This will bring balance and harmony to all aspects of your life. A holistic approach to planetary remedies will ensure success, peace, and prosperity in all areas.

**🔮 Planetary Influences & Their Effects:**

**• Surya (Sun) - Needs Strengthening** 🌞
- **Effects**: Lack of overall success, low self-esteem, poor leadership qualities
- **Life Impact**: Difficulty in achieving goals, lack of recognition, poor authority
- **Physical Symptoms**: Low energy, weak eyesight, heart-related issues, poor immunity

**• Shani (Saturn) - Requires Pacification** 🪐
- **Effects**: Obstacles in all areas, delays, restrictions, karmic challenges
- **Life Impact**: Blocked progress, financial setbacks, relationship difficulties
- **Physical Symptoms**: Chronic health issues, joint pain, skin problems, depression

**• Guru (Jupiter) - For Wisdom and Guidance** 🪔
- **Effects**: Lack of wisdom, poor judgment, difficulty in decision-making
- **Life Impact**: Poor life choices, lack of guidance, missed opportunities
- **Physical Symptoms**: Weight gain, liver issues, diabetes risk, mental confusion

**🪔 Comprehensive Vedic Remedies (Upayas):**

**1. Surya Upasana (Sun Worship) - Daily Practice** ☀️
• **Surya Namaskar**: Perform 12 rounds daily at sunrise
• **Surya Mantra**: Chant *"Om Hraam Hreem Hraum Sah Suryaya Namah"* 108 times daily
• **Ruby Gemstone**: Wear a natural ruby ring on your ring finger on Sunday
• **Surya Arghya**: Offer water to the Sun daily
• **Surya Puja**: Perform special Sun worship on Sundays
• **Red Items**: Wear red clothes on Sundays, donate red items

**2. Shani Shanti (Saturn Pacification) - Weekly Practice** 🪐
• **Shani Mantra**: Chant *"Om Sham Shanicharaya Namah"* 108 times on Saturdays
• **Blue Sapphire**: Wear a natural blue sapphire ring on your middle finger on Saturday
• **Black Items**: Donate black clothes, blankets, or oil on Saturdays
• **Sesame Oil Lamp**: Light a lamp with sesame oil on Saturdays
• **Shani Stotra**: Recite Shani Stotra daily
• **Blue Crystal**: Keep blue crystals for Saturn pacification

**3. Spiritual Strengthening** 🧘‍♂️
• **Gayatri Mantra**: Chant 108 times daily for spiritual strength
• **Om Namah Shivaya**: Chant 108 times daily for peace
• **Hanuman Chalisa**: Recite daily for strength and courage
• **Ghee Lamp**: Light a ghee lamp in front of Lord Ganesha daily
• **Spiritual Yantra**: Install a spiritual yantra in your home
• **Sacred Space**: Create a dedicated meditation area

**📿 Essential Mantras for Daily Practice:**

**Morning Mantras (6:00 AM):**
• *"Om Hraam Hreem Hraum Sah Suryaya Namah"* (For Sun strength) - 108 times
• *"Om Sham Shanicharaya Namah"* (For Saturn pacification) - 108 times
• *"Om Aim Hreem Shreem Lakshmi Narayanaya Namah"* (For prosperity) - 21 times

**Evening Mantras (6:00 PM):**
• *"Om Namah Shivaya"* (For peace and success) - 108 times
• *"Om Gam Ganapataye Namah"* (For removing obstacles) - 21 times
• *"Om Shanti Shanti Shanti"* (For peace) - 21 times

**⏰ Auspicious Timings for Remedies:**

**• Brahma Muhurat**: 4:00 AM - 6:00 AM (Best for spiritual practices)
**• Sandhya Kaal**: Dawn and dusk (Best for meditation)
**• Pradosh Kaal**: Evening twilight (Best for Shiva worship)
**• Surya Hora**: Sunrise time (Best for Sun remedies)

**🌿 Additional Recommendations:**

**• Fasting Schedule:**
- Sundays: Fast for Sun strength
- Saturdays: Fast for Saturn pacification
- Thursdays: Fast for Jupiter wisdom

**• Temple Visits:**
- Sundays: Visit Sun temples
- Saturdays: Visit Saturn temples
- Thursdays: Visit Jupiter temples
- Daily: Visit Hanuman temples and Shiva temples

**• Charity & Donations:**
- Sundays: Donate jaggery, wheat, red items
- Saturdays: Donate black items, oil, blankets
- Thursdays: Donate yellow items, books, sweets

**• Daily Rituals:**
- Light a ghee lamp in front of Lord Ganesha daily
- Practice meditation during Brahma Muhurat
- Recite Hanuman Chalisa daily
- Keep sacred crystals in your home

**📅 40-Day Comprehensive Remedy Schedule:**

**Week 1-2**: Focus on Sun remedies and basic spiritual practices
**Week 3-4**: Add Saturn pacification and advanced mantras
**Week 5-6**: Integrate all remedies and increase intensity

**✨ Divine Blessing:**

*May Lord Surya bless you with success and vitality, may Shani remove all obstacles and bring stability, and may Guru provide you with wisdom and guidance for a fulfilling life. Follow these remedies with faith and devotion for 40 days.*

**Jai Shree Ram! 🙏**"""
    
    # For question stages, ask one question at a time
    elif stage.startswith("question_"):
        question_number = stage.split("_")[1]
        if question_number == "1":
            return "I appreciate you sharing your concern with me. **Could you tell me how long you've been experiencing this situation?** Understanding the timeline - whether it's recent or long-term - will help me provide better guidance."
        elif question_number == "2":
            return "Thank you for sharing that timeline. **In what ways has this been impacting your life?** I'd like to understand how it affects different aspects - your career, relationships, wellbeing, peace of mind, or any other areas you feel are important to mention."
        elif question_number == "3":
            return "I see how this has been affecting you. **What steps or remedies have you already explored to address this?** This could include spiritual practices, lifestyle changes, or any other approaches you've tried."
        elif question_number == "4":
            return "Thank you for being open about your experiences. **Could you share how you're feeling emotionally about all of this?** Whether it's bringing up feelings of worry, frustration, hope, or any other emotions - understanding your emotional state will help me suggest appropriate remedies."
        elif question_number == "5":
            return "I appreciate you sharing your emotional journey. **Have you noticed any patterns or recurring signs in your life related to this situation?** These could be physical manifestations, repeated circumstances, or any notable synchronicities that stand out to you."
    
    return random.choice(responses)

def get_ai_response(messages: List[Dict[str, Any]], stage: str) -> str:
    """Get AI response based on conversation context and stage"""
    try:
        # For question stages and analysis stage, always use fallback responses to ensure proper flow
        if stage.startswith("question_") or stage == "analysis":
            user_message = ""
            if messages:
                user_message = messages[-1].get("content", "")
            return get_fallback_response(stage, user_message, messages)
        
        if not GROQ_AVAILABLE:
            # Use fallback responses
            user_message = ""
            if messages:
                user_message = messages[-1].get("content", "")
            return get_fallback_response(stage, user_message, messages)
        
        # Convert messages to LangChain format
        langchain_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
        for msg in messages[-10:]:  # Keep last 10 messages for context
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        # Add stage-specific context
        if stage == "greeting" and not messages:
            context = "This is the first message. Provide a warm welcome and ask about their concerns."
        elif stage == "understanding":
            context = "The user has shared their problem. Ask clarifying questions to better understand their situation and identify planetary influences."
        else:
            context = "Continue the conversation naturally, providing guidance and support."
        
        langchain_messages.append(HumanMessage(content=context))
        
        # Get response from LLM
        response = llm.invoke(langchain_messages)
        return response.content
        
    except Exception as e:
        print(f"Error getting AI response: {e}")
        # Fallback to rule-based responses
        user_message = ""
        if messages:
            user_message = messages[-1].get("content", "")
        return get_fallback_response(stage, user_message, messages)

def determine_stage(messages: List[Dict[str, Any]]) -> str:
    """Determine the current conversation stage"""
    if not messages:
        return "greeting"
    
    # Count user messages to determine stage
    user_messages = [msg for msg in messages if msg["role"] == "user"]
    message_count = len(user_messages)
    
    # Ask questions one by one - each question gets its own stage
    if message_count <= 1:
        return "greeting"
    elif message_count == 2:
        return "question_1"  # How long have you been facing this issue?
    elif message_count == 3:
        return "question_2"  # How does it affect your daily life?
    elif message_count == 4:
        return "question_3"  # What have you already tried?
    elif message_count == 5:
        return "question_4"  # How do you feel emotionally?
    elif message_count == 6:
        return "question_5"  # Specific symptoms or manifestations?
    elif message_count == 7:
        return "analysis"
    else:
        return "ongoing"

# System prompt for the agent (when GROQ is available)
SYSTEM_PROMPT = """You are Pandit Pradeep Kiradoo, a renowned Vedic astrologer with 15+ years of experience in Jyotish Shastra.

Your role is to:
1. Welcome users warmly and professionally
2. Ask ONLY ONE question at a time to understand their situation
3. Wait for their response before asking the next question
4. After collecting all information, provide detailed astrological remedies
5. Focus on planetary influences and their effects on life
6. Offer practical guidance while maintaining cultural sensitivity

CRITICAL RULES:
- ALWAYS ask ONLY ONE question per response
- NEVER ask multiple questions at once
- Wait for user's answer before proceeding to the next question
- DO NOT ask for birth details like date, time, or place of birth
- Format all responses in proper markdown with **bold** for headings
- Provide specific astrological remedies based on Vedic principles
- Focus on planetary causes and solutions
- Maintain a supportive and guiding tone
- Use emojis sparingly but appropriately (🙏, ✨, 🌟)

CONVERSATION FLOW:
1. **Greeting**: Welcome and ask about their main concern
2. **Question 1**: "How long have you been facing this issue?"
3. **Question 2**: "How does this issue affect your daily life?"
4. **Question 3**: "What have you already tried to resolve this?"
5. **Question 4**: "How do you feel emotionally about this situation?"
6. **Question 5**: "What specific symptoms or patterns have you noticed?"
7. **Analysis**: Provide remedies only after all questions are answered

RESPONSE FORMATTING:
- Use **bold** for headings
- Use bullet points (• or -) for lists
- Use proper markdown formatting
- Structure remedies clearly with numbered lists

Remember: Ask ONE question at a time and wait for the user's response."""

# Pydantic models for API
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    stage: str
    suggestions: List[str]

@app.get("/")
async def root():
    return {
        "message": "Welcome to Pandit Pradeep Kiradoo's Astrology API",
        "version": "2.0.0",
        "features": ["problem_understanding", "astrological_remedies", "planetary_analysis"],
        "groq_available": GROQ_AVAILABLE
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "astrology_chatbot_v2",
        "groq_available": GROQ_AVAILABLE
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_pandit(request: ChatRequest):
    try:
        # Get or create session
        session_id = request.session_id or f"session_{len(sessions) + 1}"
        if session_id not in sessions:
            sessions[session_id] = AstrologyState()
            sessions[session_id].session_id = session_id
        
        state = sessions[session_id]
        
        # Add user messages to state
        for msg in request.messages:
            if msg.role == "user":
                state.messages.append({
                    "role": "user",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Determine current stage
        current_stage = determine_stage(state.messages)
        state.current_stage = current_stage
        
        # Get AI response
        ai_response = get_ai_response(state.messages, current_stage)
        
        # Add AI response to state
        state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # If we're in analysis stage, mark that remedies have been provided
        if current_stage == "analysis":
            state.remedies_provided = True
        
        # Generate suggestions based on stage
        suggestions = []
        if current_stage == "greeting":
            suggestions = [
                "I'm having career-related issues",
                "I'm facing problems in my relationships",
                "I'm experiencing financial difficulties",
                "I have health concerns"
            ]
        elif current_stage == "question_1":
            suggestions = [
                "A few weeks",
                "Several months",
                "Over a year",
                "Just recently started"
            ]
        elif current_stage == "question_2":
            suggestions = [
                "Affects my work performance",
                "Impacts my relationships",
                "Affects my health",
                "Affects my sleep"
            ]
        elif current_stage == "question_3":
            suggestions = [
                "I've tried meditation",
                "I've prayed and done puja",
                "I've consulted doctors",
                "I've tried changing my routine"
            ]
        elif current_stage == "question_4":
            suggestions = [
                "I feel stressed and anxious",
                "I feel frustrated and angry",
                "I feel hopeless",
                "I feel confused"
            ]
        elif current_stage == "question_5":
            suggestions = [
                "Recurring arguments",
                "Sleep problems",
                "Loss of appetite",
                "Difficulty concentrating"
            ]
        elif current_stage == "analysis":
            suggestions = [
                "Thank you for the remedies",
                "How long should I follow these?",
                "Can you explain more about the mantras?",
                "Thank you, I'll start following these"
            ]
        else:
            suggestions = [
                "Thank you for your guidance",
                "I have another question",
                "Can you help with something else?",
                "Thank you, that's all I needed"
            ]
        
        return ChatResponse(
            message=ai_response,
            session_id=session_id,
            stage=current_stage,
            suggestions=suggestions[:4]
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if session_id in sessions:
        state = sessions[session_id]
        return {
            "session_id": session_id,
            "message_count": len(state.messages),
            "stage": state.current_stage,
            "problem_understood": state.problem_understood,
            "remedies_provided": state.remedies_provided
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
